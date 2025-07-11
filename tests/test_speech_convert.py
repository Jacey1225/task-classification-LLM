import unittest
import unittest.mock as mock
import speech_recognition as sr
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from SpeechConvert.SpeechConvert import convert_speech, convert_speech_with_timeout, convert_speech_from_file, recognizer


class TestSpeechConvert(unittest.TestCase):
    """Test cases for the SpeechConvert module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_audio_text = "Hello world"
        self.test_audio_file = "test_audio.wav"

    @mock.patch('speech_recognition.Microphone')
    @mock.patch('speech_recognition.Recognizer.listen')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    @mock.patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_convert_speech_success(self, mock_adjust, mock_recognize, mock_listen, mock_microphone):
        """Test successful speech recognition."""
        # Mock the microphone context manager
        mock_source = mock.MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_listen.return_value = mock_audio
        
        # Mock successful recognition
        mock_recognize.return_value = self.test_audio_text
        
        # Test the function
        result = convert_speech()
        
        # Assertions
        self.assertEqual(result, self.test_audio_text)
        mock_adjust.assert_called_once_with(mock_source)
        mock_listen.assert_called_once_with(mock_source)
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    @mock.patch('speech_recognition.Microphone')
    @mock.patch('speech_recognition.Recognizer.listen')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    @mock.patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_convert_speech_unknown_value_error(self, mock_adjust, mock_recognize, mock_listen, mock_microphone):
        """Test handling of UnknownValueError."""
        # Mock the microphone context manager
        mock_source = mock.MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_listen.return_value = mock_audio
        
        # Mock recognition failure
        mock_recognize.side_effect = sr.UnknownValueError()
        
        # Test the function
        result = convert_speech()
        
        # Assertions
        self.assertEqual(result, "")
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    @mock.patch('speech_recognition.Microphone')
    @mock.patch('speech_recognition.Recognizer.listen')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    @mock.patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_convert_speech_request_error(self, mock_adjust, mock_recognize, mock_listen, mock_microphone):
        """Test handling of RequestError."""
        # Mock the microphone context manager
        mock_source = mock.MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_listen.return_value = mock_audio
        
        # Mock request error
        mock_recognize.side_effect = sr.RequestError("API unavailable")
        
        # Test the function
        result = convert_speech()
        
        # Assertions
        self.assertEqual(result, "")
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    @mock.patch('speech_recognition.Microphone')
    @mock.patch('speech_recognition.Recognizer.listen')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    @mock.patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_convert_speech_with_timeout_success(self, mock_adjust, mock_recognize, mock_listen, mock_microphone):
        """Test successful speech recognition with timeout."""
        # Mock the microphone context manager
        mock_source = mock.MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_listen.return_value = mock_audio
        
        # Mock successful recognition
        mock_recognize.return_value = self.test_audio_text
        
        # Test the function
        result = convert_speech_with_timeout(timeout=3, phrase_timeout=2)
        
        # Assertions
        self.assertEqual(result, self.test_audio_text)
        mock_adjust.assert_called_once_with(mock_source, duration=1)
        mock_listen.assert_called_once_with(mock_source, timeout=3, phrase_time_limit=2)
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    @mock.patch('speech_recognition.Microphone')
    @mock.patch('speech_recognition.Recognizer.listen')
    @mock.patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_convert_speech_with_timeout_wait_timeout_error(self, mock_adjust, mock_listen, mock_microphone):
        """Test handling of WaitTimeoutError."""
        # Mock the microphone context manager
        mock_source = mock.MagicMock()
        mock_microphone.return_value.__enter__.return_value = mock_source
        mock_microphone.return_value.__exit__.return_value = None
        
        # Mock timeout error
        mock_listen.side_effect = sr.WaitTimeoutError("timeout", None)
        
        # Test the function
        result = convert_speech_with_timeout(timeout=1)
        
        # Assertions
        self.assertEqual(result, "")
        mock_listen.assert_called_once_with(mock_source, timeout=1, phrase_time_limit=1)

    @mock.patch('speech_recognition.AudioFile')
    @mock.patch('speech_recognition.Recognizer.record')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    def test_convert_speech_from_file_success(self, mock_recognize, mock_record, mock_audio_file):
        """Test successful speech recognition from file."""
        # Mock the audio file context manager
        mock_source = mock.MagicMock()
        mock_audio_file.return_value.__enter__.return_value = mock_source
        mock_audio_file.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_record.return_value = mock_audio
        
        # Mock successful recognition
        mock_recognize.return_value = self.test_audio_text
        
        # Test the function
        result = convert_speech_from_file(self.test_audio_file)
        
        # Assertions
        self.assertEqual(result, self.test_audio_text)
        mock_audio_file.assert_called_once_with(self.test_audio_file)
        mock_record.assert_called_once_with(mock_source)
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    @mock.patch('speech_recognition.AudioFile')
    @mock.patch('speech_recognition.Recognizer.record')
    @mock.patch('speech_recognition.Recognizer.recognize_google')
    def test_convert_speech_from_file_unknown_value_error(self, mock_recognize, mock_record, mock_audio_file):
        """Test handling of UnknownValueError when processing file."""
        # Mock the audio file context manager
        mock_source = mock.MagicMock()
        mock_audio_file.return_value.__enter__.return_value = mock_source
        mock_audio_file.return_value.__exit__.return_value = None
        
        # Mock audio data
        mock_audio = mock.MagicMock()
        mock_record.return_value = mock_audio
        
        # Mock recognition failure
        mock_recognize.side_effect = sr.UnknownValueError()
        
        # Test the function
        result = convert_speech_from_file(self.test_audio_file)
        
        # Assertions
        self.assertEqual(result, "")
        mock_recognize.assert_called_once_with(mock_audio, language="en-US")

    def test_recognizer_instance(self):
        """Test that recognizer is properly instantiated."""
        self.assertIsInstance(recognizer, sr.Recognizer)


class TestSpeechConvertIntegration(unittest.TestCase):
    """Integration tests for SpeechConvert module (requires actual audio hardware)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.skip_integration = not self._audio_hardware_available()
    
    def _audio_hardware_available(self):
        """Check if audio hardware is available for testing."""
        try:
            with sr.Microphone() as source:
                pass
            return True
        except (OSError, AttributeError):
            return False
    
    @unittest.skipIf(True, "Integration test - requires manual audio input")
    def test_convert_speech_integration(self):
        """Integration test for convert_speech (requires manual speaking)."""
        if self.skip_integration:
            self.skipTest("Audio hardware not available")
        
        print("\nSpeak something into the microphone...")
        result = convert_speech()
        self.assertIsInstance(result, str)
        print(f"Result: '{result}'")
    
    @unittest.skipIf(True, "Integration test - requires manual audio input")
    def test_convert_speech_with_timeout_integration(self):
        """Integration test for convert_speech_with_timeout (requires manual speaking)."""
        if self.skip_integration:
            self.skipTest("Audio hardware not available")
        
        print("\nSpeak something within 3 seconds...")
        result = convert_speech_with_timeout(timeout=3, phrase_timeout=2)
        self.assertIsInstance(result, str)
        print(f"Result: '{result}'")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
