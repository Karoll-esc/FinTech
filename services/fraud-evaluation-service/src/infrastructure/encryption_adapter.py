"""
EncryptionAdapter - AES-256 Encryption Implementation
Implementa el puerto EncryptionService con cryptography library

Seguridad PCI DSS:
- AES-256 en modo CBC
- IV aleatorio para cada encriptación
- PKCS7 padding
- IV incluido en el ciphertext para desencriptación
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from src.application.ports.card_ports import EncryptionService


class EncryptionAdapter(EncryptionService):
    """
    Adaptador de encriptación usando AES-256 CBC mode
    
    El IV (Initialization Vector) se incluye en el ciphertext encodeado en base64:
    format: base64(IV + ciphertext)
    
    Esto permite desencriptación sin almacenar el IV por separado.
    """
    
    def __init__(self, key: bytes = None):
        """
        Inicializa el adaptador con una clave AES-256
        
        Args:
            key: Clave de 32 bytes para AES-256
                 Si no se proporciona, se usa variable de entorno 'ENCRYPTION_KEY'
        """
        if key is None:
            # Obtener clave de variable de entorno
            key_str = os.getenv('ENCRYPTION_KEY')
            if not key_str:
                # Para testing: usar una clave default (en producción: NUNCA hacer esto)
                key_str = os.getenv('ENCRYPTION_KEY', 'default-key-32-bytes-12345678')
            
            # Asegurar que tiene exactamente 32 bytes para AES-256
            if len(key_str) < 32:
                key_str = key_str.ljust(32, '0')  # Padding con ceros
            key_str = key_str[:32]  # Truncar si es más largo
            key = key_str.encode('utf-8')
        
        assert len(key) == 32, "Encryption key must be 32 bytes for AES-256"
        self.key = key
    
    async def encrypt(self, plaintext: str) -> str:
        """
        Encripta un string usando AES-256 CBC
        
        Args:
            plaintext: Texto a encriptar
            
        Returns:
            str: base64(IV + ciphertext)
        """
        # Convertir plaintext a bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Generar IV aleatorio de 16 bytes
        iv = os.urandom(16)
        
        # Aplicar PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext_bytes) + padder.finalize()
        
        # Crear cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encriptar
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combinar IV + ciphertext y encodear en base64
        encrypted_data = iv + ciphertext
        encoded = base64.b64encode(encrypted_data).decode('utf-8')
        
        return encoded
    
    async def decrypt(self, ciphertext: str) -> str:
        """
        Desencripta un string encriptado con encrypt()
        
        Args:
            ciphertext: base64(IV + ciphertext)
            
        Returns:
            str: Texto original desencriptado
        """
        # Decodificar base64
        encrypted_data = base64.b64decode(ciphertext.encode('utf-8'))
        
        # Extraer IV y ciphertext
        iv = encrypted_data[:16]
        ciphertext_bytes = encrypted_data[16:]
        
        # Crear cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Desencriptar
        padded_data = decryptor.update(ciphertext_bytes) + decryptor.finalize()
        
        # Remover PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
        
        # Convertir bytes a string
        plaintext = plaintext_bytes.decode('utf-8')
        
        return plaintext
