import base64
from cryptography.fernet import Fernet
from config import settings


class EncryptionService:
    """Service for encrypting/decrypting data at rest (HIPAA compliance)"""

    def __init__(self):
        # Use the encryption key from settings
        # In production, this should be a proper 32-byte base64-encoded key
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt_file(self, file_path: str, output_path: str) -> str:
        """
        Encrypt a file and save to output path

        Args:
            file_path: Path to file to encrypt
            output_path: Path to save encrypted file

        Returns:
            Path to encrypted file
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        encrypted_data = self.cipher.encrypt(data)

        with open(output_path, 'wb') as f:
            f.write(encrypted_data)

        return output_path

    def decrypt_file(self, file_path: str, output_path: str) -> str:
        """
        Decrypt a file and save to output path

        Args:
            file_path: Path to encrypted file
            output_path: Path to save decrypted file

        Returns:
            Path to decrypted file
        """
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)

        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path

    def encrypt_text(self, text: str) -> str:
        """
        Encrypt text data

        Args:
            text: Text to encrypt

        Returns:
            Encrypted text (base64 encoded)
        """
        encrypted = self.cipher.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypt text data

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted text
        """
        encrypted = base64.b64decode(encrypted_text.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()


# Global encryption service instance
encryption_service = EncryptionService()
