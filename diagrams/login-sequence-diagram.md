# Login-sequence diagram

```mermaid

sequenceDiagram
    actor User
    participant WebUI as ITM CyberRange Web Portal
    participant AuthSvc as OAuth2 Auth Service
    participant API as Backend API
    participant DB as Local Database
    participant Session as Session Manager

    User->>WebUI: Navigate to Login Page
    WebUI->>User: Present Login Form

    User->>WebUI: Submit Credentials
    WebUI->>AuthSvc: Forward Auth Request

    alt Authentication Failed
        AuthSvc-->>WebUI: Auth Failure (401)
        WebUI-->>User: Display Error Message
    else Authentication Successful
        AuthSvc-->>WebUI: OAuth2 Token Returned
        WebUI->>API: Send Token + User Identity

        API->>DB: Query — Does user record exist?

        alt New User - First Login
            DB-->>API: No Record Found
            API->>API: Generate Unique User Hash (SHA-256 / UUID)
            API->>DB: CREATE user record
            API->>DB: STORE OAuth2 token
            API->>DB: LOG first login timestamp
            API->>DB: INITIALIZE user profile & permissions
            DB-->>API: New Account Created

        else Existing User (Returning Login)
            DB-->>API: User Record Found
            API->>DB: UPDATE last login timestamp
            API->>DB: REFRESH OAuth2 token
            API->>DB: APPEND login event to audit log
            DB-->>API: Account Updated
        end

        API->>Session: Create authenticated session
        Session-->>API: Session token issued
        API-->>WebUI: Return session token + user profile

        WebUI->>User: Present Welcome Screen
    end
