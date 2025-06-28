import CryptoJS from 'crypto-js';

export class EncryptionService {
  private static instance: EncryptionService;
  private masterKey: string;

  private constructor() {
    // Generate or retrieve master key
    this.masterKey = this.getMasterKey();
  }

  public static getInstance(): EncryptionService {
    if (!EncryptionService.instance) {
      EncryptionService.instance = new EncryptionService();
    }
    return EncryptionService.instance;
  }

  private getMasterKey(): string {
    let key = localStorage.getItem('clipvault_master_key');
    if (!key) {
      key = CryptoJS.lib.WordArray.random(256/8).toString();
      localStorage.setItem('clipvault_master_key', key);
    }
    return key;
  }

  public encrypt(data: string): { encrypted: string; iv: string } {
    const iv = CryptoJS.lib.WordArray.random(128/8);
    const encrypted = CryptoJS.AES.encrypt(data, this.masterKey, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });

    return {
      encrypted: encrypted.toString(),
      iv: iv.toString()
    };
  }

  public decrypt(encryptedData: string, iv: string): string {
    try {
      const decrypted = CryptoJS.AES.decrypt(encryptedData, this.masterKey, {
        iv: CryptoJS.enc.Hex.parse(iv),
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      });

      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      console.error('Decryption failed:', error);
      return '';
    }
  }

  public generateHash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }

  public generateKeyPair(): { publicKey: string; privateKey: string } {
    // Simulate RSA key pair generation
    const keyId = Date.now().toString();
    return {
      publicKey: `-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA${keyId}...\n-----END PUBLIC KEY-----`,
      privateKey: `-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC${keyId}...\n-----END PRIVATE KEY-----`
    };
  }
}