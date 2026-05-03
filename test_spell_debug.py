"""
Debug test for LanguageTool and TextBlob
"""

print("Testing LanguageTool initialization...\n")

try:
    import language_tool_python
    print("✓ language_tool_python imported successfully")
    
    tool = language_tool_python.LanguageTool('en-US')
    print("✓ LanguageTool initialized")
    
    # Test basic correction
    test_text = "wht is this"
    print(f"\nTest text: '{test_text}'")
    
    matches = tool.check(test_text)
    print(f"Found {len(matches)} errors")
    
    for match in matches:
        print(f"\n  Error: {match.message}")
        print(f"  Position: {match.offset}-{match.offset + match.length}")
        print(f"  Word: '{test_text[match.offset:match.offset + match.length]}'")
        print(f"  Suggestions: {match.replacements[:3] if match.replacements else 'None'}")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Testing TextBlob...\n")

try:
    from textblob import TextBlob
    print("✓ TextBlob imported successfully")
    
    test_words = ["demnetia", "alzeimer", "memry", "worie"]
    
    for word in test_words:
        blob = TextBlob(word)
        corrected = str(blob.correct())
        print(f"  '{word}' → '{corrected}'")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
