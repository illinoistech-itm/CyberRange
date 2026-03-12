**Quick Answer:** To add a .crt file to the Windows Certificate Store, open the **MMC (Microsoft Management Console)**, add the **Certificates snap-in** for either the current user or local computer, then use the **Import Wizard** to load your .crt file into the appropriate store (e.g., _Trusted Root Certification Authorities_ or _Personal_).

### **Step-by-Step Guide**

- **Open MMC**
  - Press **Win + R**, type mmc, and hit **Enter**.
- **Add the Certificates Snap-in**
  - In MMC, go to **File > Add/Remove Snap-in**.
  - Select **Certificates** and click **Add**.
  - Choose either:
    - **My user account** → adds to the _Current User_ store.
    - **Computer account** → adds to the _Local Computer_ store.
  - Click **Finish**, then **OK**.
- **Navigate to the Right Store**
  - Expand **Certificates (Current User)** or **Certificates (Local Computer)**.
  - Common destinations:
    - **Trusted Root Certification Authorities** → for root CA certificates.
    - **Intermediate Certification Authorities** → for intermediate CA certs.
    - **Personal** → for end-user or server certificates.
- **Import the Certificate**
  - Right-click the target folder (e.g., _Trusted Root Certification Authorities > Certificates_).
  - Select **All Tasks > Import**.
  - In the **Certificate Import Wizard**:
    - Click **Next**.
    - Browse to your .crt file.
    - Select **Place all certificates in the following store** and confirm the correct store.
    - Click **Next > Finish**.
- **Verify Import**
  - You should see a success message.
  - The certificate will now appear in the chosen store.

<https://copilot.microsoft.com/shares/vkhggaqx1vT99t9oyRqa8>

<https://learn.microsoft.com/en-us/biztalk/adapters-and-accelerators/accelerator-swift/adding-certificates-to-the-certificates-store-on-the-client>
