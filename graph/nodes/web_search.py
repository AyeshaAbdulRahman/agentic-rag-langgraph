"""
graph/nodes/web_search.py - Node 6b: Web Search Fallback

Intelligent web search with:
  - Query optimization
  - Trusted-source filtering for medical safety
  - Deduplication
  - Relevance scoring
  - Timeout handling
  - Better error handling

When document retrieval yields no relevant results, searches DuckDuckGo
(free, no API key needed). This is a fallback when filtered_documents empty.
"""

import hashlib
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

from graph.state import AgentState


_search_cache = {}
CACHE_TTL = 15 * 60

QUERY_BOOSTERS = {
    'dementia': ['statistics', 'patients', 'prevalence', 'estimated', 'incidence'],
    'alzheimer': ['symptoms', 'diagnosis', 'treatment', 'progression'],
    'cognitive': ['impairment', 'assessment', 'testing', 'screening'],
    'caregiver': ['support', 'resources', 'training', 'mental health'],
}

BLOCKED_DOMAINS = [
    'pinterest.com', 'reddit.com', 'quora.com', 'youtube.com',
    'facebook.com', 'twitter.com', 'tiktok.com', 'instagram.com',
    'ad', 'ads.', 'sponsored', 'amazon.com', 'ebay.com'
]

TRUSTED_DOMAINS = {
    'aku.edu',
    'akuh.edu',
    'alz.org',
    'alzheimers.gov',
    'alzheimers.org.uk',
    'alzheimersresearchuk.org',
    'cdc.gov',
    'clevelandclinic.org',
    'hopkinsmedicine.org',
    'mayoclinic.org',
    'medlineplus.gov',
    'nhs.uk',
    'nia.nih.gov',
    'nih.gov',
    'ninds.nih.gov',
    'who.int',
}

AUTHORITY_KEYWORDS = {
    'alzheimer',
    'association',
    'caregiver',
    'clinic',
    'dementia',
    'health',
    'hospital',
    'institute',
    'medical',
    'memory clinic',
    'ministry of health',
    'national institute',
    'neurology',
    'nhs',
    'nih',
    'public health',
    'university',
}

SUSPICIOUS_CLAIM_KEYWORDS = {
    '100% cure',
    'breakthrough cure',
    'buy now',
    'click here',
    'doctor hates',
    'guaranteed',
    'instant cure',
    'miracle',
    'overnight',
    'secret remedy',
    'shocking',
    'this one trick',
}

STRICT_WEB_TRUST_FILTER = os.getenv('STRICT_WEB_TRUST_FILTER', 'true').lower() == 'true'
MIN_WEB_RESULT_RELEVANCE = float(os.getenv('MIN_WEB_RESULT_RELEVANCE', '0.35'))


def _get_cache_key(query: str) -> str:
    return hashlib.md5(query.lower().encode()).hexdigest()


def _is_cache_valid(timestamp: float) -> bool:
    return (datetime.now().timestamp() - timestamp) < CACHE_TTL


def _check_connectivity() -> bool:
    try:
        urllib.request.urlopen('https://www.google.com', timeout=2)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return False


def _perform_web_search_with_retry(query: str, max_retries: int = 3, initial_timeout: int = 5) -> List[Dict]:
    from ddgs import DDGS

    last_error = None

    for attempt in range(max_retries):
        try:
            timeout = initial_timeout * (2 ** attempt)
            print(f"Search attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)")

            ddgs = DDGS(timeout=timeout)
            raw_results = ddgs.text(
                query,
                max_results=20,
                region='wt-wt'
            )

            print(f"Search successful on attempt {attempt + 1}")
            return raw_results

        except TimeoutError as e:
            last_error = e
            print(f"Attempt {attempt + 1} timed out (timeout: {timeout}s)")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {type(e).__name__}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

    raise last_error or Exception(f"Web search failed after {max_retries} retries")


def _optimize_query(question: str) -> str:
    query = question.strip()
    query_lower = query.lower()

    boosters = set()
    for keyword, terms in QUERY_BOOSTERS.items():
        if keyword in query_lower:
            boosters.update(terms)

    if boosters:
        query = f"{query} {' '.join(sorted(boosters)[:3])}"

    query = query.replace('?', '').strip()
    return query


def _extract_domain(url: str) -> str:
    if not url:
        return ''

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def _has_trusted_public_suffix(domain: str) -> bool:
    if not domain:
        return False

    return (
        domain.endswith('.gov')
        or '.gov.' in domain
        or domain.endswith('.edu')
        or '.edu.' in domain
        or domain.endswith('.nhs.uk')
    )


def _has_authority_signals(result: Dict) -> bool:
    haystack = ' '.join([
        result.get('title', ''),
        result.get('body', ''),
        result.get('href', ''),
    ]).lower()
    return any(keyword in haystack for keyword in AUTHORITY_KEYWORDS)


def _is_trusted_result(result: Dict) -> bool:
    domain = _extract_domain(result.get('href', ''))

    if domain in TRUSTED_DOMAINS:
        return True

    if _has_trusted_public_suffix(domain):
        return True

    if STRICT_WEB_TRUST_FILTER:
        return False

    return _has_authority_signals(result)


def _looks_sensational(result: Dict) -> bool:
    haystack = ' '.join([
        result.get('title', ''),
        result.get('body', ''),
    ]).lower()
    return any(keyword in haystack for keyword in SUSPICIOUS_CLAIM_KEYWORDS)


def _get_trust_label(result: Dict) -> str:
    domain = _extract_domain(result.get('href', ''))

    if domain in TRUSTED_DOMAINS or _has_trusted_public_suffix(domain):
        return 'high'
    if _has_authority_signals(result):
        return 'medium'
    return 'low'


def _is_quality_result(result: Dict) -> bool:
    title = result.get('title', '').lower()
    body = result.get('body', '')
    url = result.get('href', '').lower()

    if not title or len(body.strip()) < 50:
        return False

    for blocked in BLOCKED_DOMAINS:
        if blocked.lower() in url:
            return False

    spam_keywords = ['click here', 'buy now', 'sponsored', 'ad ', 'advertisement']
    for spam in spam_keywords:
        if spam in title or spam in body.lower():
            return False

    if _looks_sensational(result):
        return False

    if not _is_trusted_result(result):
        return False

    if len(body.split()) < 10:
        return False

    return True


def _calculate_relevance(result: Dict, query: str) -> float:
    title = result.get('title', '').lower()
    body = result.get('body', '').lower()
    query_terms = set(query.lower().split())

    common = {'the', 'a', 'an', 'is', 'and', 'or', 'in', 'of', 'to', 'for'}
    query_terms = query_terms - common

    score = 0.0

    title_matches = sum(1 for term in query_terms if term in title)
    score += title_matches * 0.4

    body_matches = sum(1 for term in query_terms if term in body)
    score += body_matches * 0.1

    max_score = len(query_terms) * 0.4 + len(query_terms) * 0.1
    if max_score > 0:
        score = min(1.0, score / max_score)

    return score


def _deduplicate_results(results: List[Dict]) -> List[Dict]:
    seen_titles = set()
    unique = []

    for result in results:
        title = result.get('title', '').strip()
        title_key = re.sub(r'\s+', ' ', title.lower())[:100]

        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(result)

    return unique


def web_search_node(state: AgentState) -> AgentState:
    if state.filtered_documents:
        state.used_web_search = False
        return state

    if not _check_connectivity():
        print('No internet connection available')
        state.web_search_results = None
        state.used_web_search = False
        return state

    try:
        search_query = _optimize_query(state.corrected_question)
        cache_key = _get_cache_key(search_query)

        if cache_key in _search_cache:
            cached = _search_cache[cache_key]
            if _is_cache_valid(cached['timestamp']):
                print('Using cached web search results (15min TTL)')
                state.web_search_results = cached['results']
                state.used_web_search = True
                return state

        print(f'Search query: {search_query}')

        raw_results = _perform_web_search_with_retry(search_query, max_retries=3)
        print(f'Raw results received: {len(raw_results)}')

        filtered = [r for r in raw_results if _is_quality_result(r)]
        print(f'After trust and quality filter: {len(filtered)}')

        deduplicated = _deduplicate_results(filtered)
        print(f'After deduplication: {len(deduplicated)}')

        scored = [
            {
                **r,
                '_relevance': _calculate_relevance(r, search_query),
                '_trust': _get_trust_label(r),
            }
            for r in deduplicated
        ]
        scored = [r for r in scored if r['_relevance'] >= MIN_WEB_RESULT_RELEVANCE]
        scored.sort(key=lambda x: x['_relevance'], reverse=True)

        final_results = scored[:6]

        if not final_results:
            print('No trustworthy results remained after filtering')
            state.web_search_results = None
            state.used_web_search = False
            return state

        formatted_results = _format_results_for_llm(final_results)

        _search_cache[cache_key] = {
            'results': formatted_results,
            'timestamp': datetime.now().timestamp()
        }

        state.web_search_results = formatted_results
        state.used_web_search = True

        print(f'Final trusted results: {len(final_results)}')
        for i, result in enumerate(final_results, 1):
            print(
                f"  {i}. [{result['_relevance']:.2f}] "
                f"[trust={result.get('_trust', 'low')}] "
                f"{result.get('title', '')[:70]}..."
            )

    except TimeoutError:
        print('Web search timed out after 3 retries - possible network issue')
        print('Tip: Check your internet connection or firewall settings')
        state.web_search_results = None
        state.used_web_search = False
    except Exception as e:
        error_msg = str(e)
        print(f'Web search error: {type(e).__name__}: {error_msg[:100]}')

        if 'Brave' in error_msg or 'search.brave.com' in error_msg:
            print('Tip: Search backend is unreachable. Retrying may help.')
        elif 'Connection' in error_msg or 'URLError' in error_msg:
            print('Tip: Connection issue. Check firewall, proxy, or VPN settings.')
        else:
            print('Tip: Try again in a moment. If issue persists, check internet connection.')

        state.web_search_results = None
        state.used_web_search = False

    return state


def _format_results_for_llm(results: List[Dict]) -> str:
    formatted = ''

    for i, result in enumerate(results, 1):
        relevance = result.get('_relevance', 0)
        relevance_bar = '#' * int(relevance * 5) + '-' * (5 - int(relevance * 5))
        trust_label = result.get('_trust', 'low').upper()
        domain = _extract_domain(result.get('href', ''))

        formatted += f"\n{'=' * 70}\n"
        formatted += f"[Source {i}] Relevance: {relevance_bar} ({relevance:.1%})\n"
        formatted += f"Trust: {trust_label}\n"
        formatted += f"Domain: {domain or 'N/A'}\n"
        formatted += f"Title: {result.get('title', 'N/A')}\n"
        formatted += f"URL: {result.get('href', 'N/A')}\n"
        formatted += f"Summary: {result.get('body', 'N/A')[:500]}\n"

    return formatted


if __name__ == '__main__':
    from graph.state import AgentState

    print('=' * 70)
    print('Testing Trusted Web Search Node')
    print('=' * 70)

    test_cases = [
        'What is mild cognitive impairment?',
        'How many dementia patients in Japan?',
        "What are the symptoms of Alzheimer's disease?",
    ]

    for i, query in enumerate(test_cases, 1):
        print(f"\nTest {i}: {query}")
        print('-' * 70)

        state = AgentState(
            question=query,
            corrected_question=query
        )

        result = web_search_node(state)

        print(f"\nWeb Search Used: {result.used_web_search}")

        if result.web_search_results:
            print('\nResults Preview:')
            print(result.web_search_results[:800])
        else:
            print('\nNo trustworthy results found')

        print('\n' + '=' * 70)
