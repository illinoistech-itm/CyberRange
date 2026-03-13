**Quick Answer:** On macOS, you add a .crt file to the certificate store using **Keychain Access** or the **Terminal**. The GUI method is easiest: open **Keychain Access**, drag the .crt file into the desired keychain (usually _System_ or _Login_), and set its trust settings.

### **🔑 Method 1: Using Keychain Access (GUI)**

**Open Keychain Access**

Press **Cmd + Space**, type Keychain Access, and hit **Enter**.

**Choose the Keychain**

Select either:

**System** → applies to all users on the Mac.

**Login** → applies only to your user account.

**Import the Certificate**

Drag and drop the .crt file into the Keychain Access window, or go to **File > Import Items** and select your .crt.

**Set Trust Settings (Optional)**

Double-click the certificate.

Expand the **Trust** section.

Choose **Always Trust** (or other trust level depending on your needs).

Close the window; you may be prompted for your admin password.

Sources: Apple Support

### **💻 Method 2: Using Terminal (Command Line)**

For automation or scripting, you can use the security command:

bash

sudo security add-trusted-cert -d -r trustRoot \\  
\-k /Library/Keychains/System.keychain /path/to/your/certificate.crt

\-d → marks the certificate as trusted.

\-r trustRoot → specifies it as a root certificate.

\-k → points to the keychain (System or Login).

Replace /path/to/your/certificate.crt with the actual path.

This adds the certificate to the **System keychain** and sets it as trusted.

### **📌 Notes & Best Practices**

**System vs. Login Keychain:** Use _System_ for certificates that should be trusted by all users and system services. Use _Login_ for user-specific certs.

**File Formats:** macOS supports .crt, .cer, .pem, and .p12 (PKCS#12 with private key).

**Admin Rights:** Adding to the _System_ keychain requires administrator privileges.

**Verification:**

<https://copilot.microsoft.com/shares/VdcGDW7vu9Zr7Txu97hX1>
