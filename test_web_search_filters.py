import unittest

from graph.nodes.web_search import (
    _extract_domain,
    _get_trust_label,
    _is_quality_result,
    _is_trusted_result,
)


class WebSearchFilterTests(unittest.TestCase):
    def test_trusted_medical_domain_is_allowed(self):
        result = {
            'title': "Alzheimer's disease - Symptoms and causes",
            'body': 'Mayo Clinic explains the symptoms, causes, and progression of Alzheimer\'s disease in detail.',
            'href': 'https://www.mayoclinic.org/diseases-conditions/alzheimers-disease/symptoms-causes/syc-20350447',
        }

        self.assertEqual(_extract_domain(result['href']), 'mayoclinic.org')
        self.assertTrue(_is_trusted_result(result))
        self.assertTrue(_is_quality_result(result))
        self.assertEqual(_get_trust_label(result), 'high')

    def test_social_or_low_trust_result_is_rejected(self):
        result = {
            'title': 'Miracle cure for dementia revealed',
            'body': 'Click here to discover the shocking secret remedy doctors do not want you to know about.',
            'href': 'https://www.youtube.com/watch?v=fake',
        }

        self.assertFalse(_is_trusted_result(result))
        self.assertFalse(_is_quality_result(result))

    def test_public_health_domain_is_allowed(self):
        result = {
            'title': 'Dementia overview',
            'body': 'This public health guidance explains symptoms, risk factors, diagnosis, and support pathways for dementia care.',
            'href': 'https://www.nia.nih.gov/health/alzheimers-and-dementia/what-is-dementia',
        }

        self.assertTrue(_is_trusted_result(result))
        self.assertTrue(_is_quality_result(result))
        self.assertEqual(_get_trust_label(result), 'high')


if __name__ == '__main__':
    unittest.main()
