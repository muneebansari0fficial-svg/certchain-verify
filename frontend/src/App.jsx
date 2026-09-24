import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [activePage, setActivePage] = useState(
    () => localStorage.getItem("activePage") || "verify"
  );
  const [autoHash, setAutoHash] = useState(null);

  const [isLoggedIn, setIsLoggedIn] = useState(
    () => localStorage.getItem("isLoggedIn") === "true"
  );

  const [institutionName, setInstitutionName] = useState(
    () => localStorage.getItem("institutionName") || ""
  );

  useEffect(() => {
    const path = window.location.pathname;

    if (path.startsWith("/verify/")) {
      const hash = path.replace("/verify/", "").trim();

      if (hash.length === 64) {
        setAutoHash(hash);
        setActivePage("verify");
      }
    }
  }, []);

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });

    localStorage.setItem("activePage", activePage);
  }, [activePage]);

  const handleLogin = (name) => {
    setIsLoggedIn(true);
    setInstitutionName(name);

    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("institutionName", name);

    setActivePage("issue");
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setInstitutionName("");

    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("institutionName");
    localStorage.removeItem("activePage");

    setActivePage("verify");
  };

  return (
    <div className="app">

      <nav className="navbar">
        <div className="nav-brand">CertChain Verify</div>

        <div className="nav-links">

          <button
            className={activePage === "verify" ? "nav-button active-nav" : "nav-button"}
            onClick={() => setActivePage("verify")}
          >
            Verify
          </button>

          {isLoggedIn && (
            <button
              className={activePage === "issue" ? "nav-button active-nav" : "nav-button"}
              onClick={() => setActivePage("issue")}
            >
              Issue Certificate
            </button>
          )}

          {isLoggedIn && (
            <button
              className={activePage === "admin" ? "nav-button active-nav" : "nav-button"}
              onClick={() => setActivePage("admin")}
            >
              🛠️ Admin Panel
            </button>
          )}

          <button
            className={activePage === "wallet" ? "nav-button active-nav" : "nav-button"}
            onClick={() => setActivePage("wallet")}
          >
            Student Wallet
          </button>

          {isLoggedIn ? (
            <button
              className="nav-button"
              onClick={handleLogout}
              style={{
                background: "rgba(239, 68, 68, 0.15)",
                color: "#fca5a5"
              }}
            >
              Logout ({institutionName})
            </button>
          ) : (
            <button
              className={activePage === "login" ? "nav-button active-nav" : "nav-button"}
              onClick={() => setActivePage("login")}
              style={{
                background: "rgba(34, 197, 94, 0.15)",
                color: "#86efac"
              }}
            >
              🔒 Institution Login
            </button>
          )}

        </div>
      </nav>

      <header className="header">
        <h1>CertChain Verify</h1>
        <p>Blockchain-Based Academic Certificate Verification System</p>
      </header>

      <main className="container">

        <div className="features">

          <div className="feature">
            <div className="feature-icon">⛓️</div>
            <div>
              <h3>Blockchain Secured</h3>
              <p>Certificate records are securely verified on blockchain.</p>
            </div>
          </div>

          <div className="feature">
            <div className="feature-icon">🤖</div>
            <div>
              <h3>AI Forensics</h3>
              <p>AI analyzes certificates for possible forgery indicators.</p>
            </div>
          </div>

          <div className="feature">
            <div className="feature-icon">📦</div>
            <div>
              <h3>IPFS Storage</h3>
              <p>Certificate documents are stored using decentralized storage.</p>
            </div>
          </div>

        </div>

        {activePage === "verify" && <VerifyPage autoHash={autoHash} />}

        {activePage === "issue" && isLoggedIn && <IssuePage />}

        {activePage === "issue" && !isLoggedIn && (
          <AccessDenied onLogin={() => setActivePage("login")} />
        )}

        {activePage === "admin" && isLoggedIn && <AdminPanel />}

        {activePage === "admin" && !isLoggedIn && (
          <AccessDenied onLogin={() => setActivePage("login")} />
        )}

        {activePage === "wallet" && <StudentWallet />}

        {activePage === "login" && (
          <LoginPage
            onLogin={handleLogin}
            onCancel={() => setActivePage("verify")}
          />
        )}

      </main>

    </div>
  );
}


/* ================================================= */
/* ACCESS DENIED */
/* ================================================= */

function AccessDenied({ onLogin }) {
  return (
    <div className="card">
      <h2>🔒 Access Denied</h2>

      <div className="coming-soon">
        <h3>Institution Access Required</h3>
        <p>
          Only authorized institutions can access this page.
          Please login with your institution credentials.
        </p>

        <button
          onClick={onLogin}
          style={{ marginTop: "20px" }}
        >
          Go to Login
        </button>
      </div>
    </div>
  );
}


/* ================================================= */
/* LOGIN PAGE */
/* ================================================= */

function LoginPage({ onLogin, onCancel }) {

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    setUsername("");
    setPassword("");
    setError("");
    setShowPassword(false);
  }, []);

  const handleSubmit = async () => {

    if (!username.trim()) {
      setError("Please enter username");
      return;
    }

    if (!password.trim()) {
      setError("Please enter password");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.status === "success") {
        onLogin(data.institution_name);
      } else {
        setError(data.message || "Login failed");
      }

    } catch (err) {
      setError("Could not connect to the backend");
    }

    setLoading(false);
  };

  return (
    <div className="login-wrapper">

      <div className="login-card">

        <div className="login-icon-box">
          🔐
        </div>

        <h2 className="login-title">
          Institution Login
        </h2>

        <p className="login-subtitle">
          Enter your credentials to access the
          certificate issuance portal.
        </p>

        <form
          className="login-form"
          autoComplete="off"
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >

          <label className="login-label">
            Username
          </label>

          <div className="login-input-wrapper">

            <span className="login-input-icon">
              👤
            </span>

            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="login-input"
              autoComplete="off"
              name="institution-username"
            />

          </div>

          <label className="login-label">
            Password
          </label>

          <div className="login-input-wrapper">

            <span className="login-input-icon">
              🔑
            </span>

            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter institution password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input"
              autoComplete="new-password"
              name="institution-password"
            />

            <button
              type="button"
              className="login-eye-btn"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "🙈" : "👁️"}
            </button>

          </div>

          {error && (
            <div className="login-error">
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            className="login-submit-btn"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

          <button
            type="button"
            className="login-cancel-btn"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>

        </form>

        <p className="login-hint">
          🔒 Authorized personnel only
        </p>

      </div>

    </div>
  );
}


/* ================================================= */
/* VERIFY PAGE */
/* ================================================= */

function VerifyPage({ autoHash }) {

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ✅ Page khulte hi clear karo
  useEffect(() => {
    setFile(null);
    setResult(null);
  }, []);

  useEffect(() => {
    if (autoHash) {
      autoVerify(autoHash);
    }
  }, [autoHash]);

  const autoVerify = async (hash) => {

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/verify/${hash}`);
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: "error",
        message: "Could not connect to the backend.",
      });
    }

    setLoading(false);
  };

  const verifyCertificate = async () => {

    if (!file) {
      alert("Please select a certificate PDF first.");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/verify", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: "error",
        message: "Could not connect to the backend. Make sure FastAPI is running.",
      });
    }

    setLoading(false);
  };

  return (
    <>
      <div className="card">

        <h2>Verify Certificate</h2>

        <p className="description">
          Upload an academic certificate PDF to verify its authenticity
          using blockchain and AI.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            verifyCertificate();
          }}
        >

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => {
              setFile(e.target.files[0]);
              setResult(null);
            }}
          />

          {file && (
            <p className="file-name">Selected: {file.name}</p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Verifying..." : "Verify Certificate"}
          </button>

        </form>

      </div>

      {result && (
        <div className="result-card">

          <h2>Verification Result</h2>

          {result.status === "error" ? (
            <p className="error">{result.message}</p>
          ) : (
            <>
              <div className="status">{result.certificate_status}</div>

              <div className="details">

                {result.filename && (
                  <p>
                    <strong>File:</strong>
                    {result.filename}
                  </p>
                )}

                <p>
                  <strong>SHA-256:</strong>
                  {result.sha256}
                </p>

                {result.blockchain && (
                  <>
                    <p>
                      <strong>Blockchain Registered:</strong>
                      {result.blockchain.exists ? "Yes" : "No"}
                    </p>

                    <p>
                      <strong>Blockchain Valid:</strong>
                      {result.blockchain.valid ? "Yes" : "No"}
                    </p>

                    <p>
                      <strong>Issuer:</strong>
                      {result.blockchain.issuer_name || "Not available"}
                    </p>

                    <p>
                      <strong>AI Risk Score:</strong>
                      {result.blockchain.ai_risk_score}
                    </p>
                  </>
                )}

                {result.ai && (
                  <>
                    <p>
                      <strong>AI Analysis:</strong>
                      {result.ai.analysis}
                    </p>

                    {result.ai.risk_category && (
                      <p>
                        <strong>AI Risk:</strong>
                        {result.ai.risk_category}
                      </p>
                    )}
                  </>
                )}

              </div>
            </>
          )}

        </div>
      )}
    </>
  );
}


/* ================================================= */
/* ISSUE PAGE */
/* ================================================= */

function IssuePage() {

  const [file, setFile] = useState(null);
  const [studentRef, setStudentRef] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const issueCertificate = async () => {

    if (!file) {
      alert("Please select a certificate PDF first.");
      return;
    }

    if (!studentRef.trim()) {
      alert("Please enter student reference.");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("student_ref", studentRef);

    try {
      const response = await fetch("http://127.0.0.1:8000/issue", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: "error",
        message: "Could not connect to the backend. Make sure FastAPI is running.",
      });
    }

    setLoading(false);
  };

  return (
    <div className="card">

      <h2>Issue Certificate</h2>

      <p className="description">
        Authorized institutions can upload an academic certificate
        and register it on blockchain.
      </p>

      <form
        className="issue-form"
        onSubmit={(e) => {
          e.preventDefault();
          issueCertificate();
        }}
      >

        <label>Student Reference</label>

        <input
          type="text"
          placeholder="e.g. 22-CS-107"
          value={studentRef}
          onChange={(e) => setStudentRef(e.target.value)}
        />

        <label>Certificate PDF</label>

        <input
          type="file"
          accept=".pdf"
          onChange={(e) => {
            setFile(e.target.files[0]);
            setResult(null);
          }}
        />

        {file && (
          <p className="file-name">Selected: {file.name}</p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Issuing Certificate..." : "Issue Certificate"}
        </button>

      </form>

      {result && (
        <div className="result-card">

          {result.status === "error" ? (
            <p className="error">{result.message}</p>
          ) : (
            <>
              <div className="status">{result.message}</div>

              <div className="details">

                <p>
                  <strong>SHA-256:</strong>
                  {result.sha256}
                </p>

                <p>
                  <strong>Student Reference:</strong>
                  {result.student_ref}
                </p>

                {result.ipfs_cid && (
                  <p>
                    <strong>IPFS CID:</strong>
                    {result.ipfs_cid}
                  </p>
                )}

                {result.tx_hash && (
                  <p>
                    <strong>Transaction Hash:</strong>
                    {result.tx_hash}
                  </p>
                )}

                <p>
                  <strong>AI Risk Score:</strong>
                  {result.ai_risk_score}
                </p>

              </div>

              {result.qr_code && (
                <div className="qr-section">

                  <h3>Certificate QR Code</h3>

                  <div className="qr-box">
                    <img
                      src={result.qr_code}
                      alt="Certificate QR Code"
                    />
                  </div>

                  {result.verification_url && (
                    <p className="qr-url">
                      {result.verification_url}
                    </p>
                  )}

                  <p className="qr-hint">
                    Scan this QR code to verify the certificate
                  </p>

                  {result.qr_pdf_url && (
                    <div style={{ marginTop: "20px" }}>
                      <a
                        href={result.qr_pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="wallet-btn"
                        style={{
                          display: "inline-block",
                          padding: "12px 22px",
                          textDecoration: "none",
                          fontSize: "13px"
                        }}
                      >
                        📥 Download PDF with QR
                      </a>
                    </div>
                  )}

                  <div style={{ marginTop: "12px" }}>
                    <a
                      href={result.qr_code}
                      download="certificate_qr.png"
                      className="wallet-btn"
                      style={{
                        display: "inline-block",
                        padding: "10px 18px",
                        textDecoration: "none",
                        fontSize: "12px",
                        background: "#1e40af"
                      }}
                    >
                      📥 Download QR (PNG)
                    </a>
                  </div>

                </div>
              )}

            </>
          )}

        </div>
      )}

    </div>
  );
}


/* ================================================= */
/* ADMIN PANEL */
/* ================================================= */

function AdminPanel() {

  const [docHash, setDocHash] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const revokeCertificate = async () => {

    if (!docHash.trim()) {
      alert("Please enter certificate document hash");
      return;
    }

    if (docHash.length !== 64) {
      alert("Document hash must be 64 characters (SHA-256)");
      return;
    }

    if (!reason.trim()) {
      alert("Please enter revoke reason");
      return;
    }

    if (!window.confirm("Are you sure you want to revoke this certificate? This action cannot be undone.")) {
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("doc_hash", docHash);
    formData.append("reason", reason);

    try {
      const response = await fetch("http://127.0.0.1:8000/revoke", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);

    } catch (error) {
      setResult({
        status: "error",
        message: "Could not connect to the backend.",
      });
    }

    setLoading(false);
  };

  return (
    <div className="card">

      <h2>🛠️ Admin Panel</h2>

      <p className="description">
        Revoke a previously issued certificate. Once revoked, the
        certificate will show as REVOKED during verification.
      </p>

      <form
        className="issue-form"
        onSubmit={(e) => {
          e.preventDefault();
          revokeCertificate();
        }}
      >

        <label>Certificate Document Hash (SHA-256)</label>

        <input
          type="text"
          placeholder="Enter 64-character document hash"
          value={docHash}
          onChange={(e) => setDocHash(e.target.value)}
        />

        <label>Revoke Reason</label>

        <input
          type="text"
          placeholder="e.g. Issued by mistake, Forgery detected"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            background: "linear-gradient(135deg, #dc2626, #b91c1c)"
          }}
        >
          {loading ? "Revoking..." : "⚠️ Revoke Certificate"}
        </button>

      </form>

      {result && (
        <div className="result-card">

          {result.status === "error" ? (
            <p className="error">{result.message}</p>
          ) : (
            <>
              <div className="status" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#fca5a5" }}>
                {result.message}
              </div>

              <div className="details">

                <p>
                  <strong>Document Hash:</strong>
                  <span className="hash">{result.doc_hash}</span>
                </p>

                <p>
                  <strong>Reason:</strong>
                  {result.reason}
                </p>

                <p>
                  <strong>Transaction Hash:</strong>
                  <span className="hash">{result.tx_hash}</span>
                </p>

              </div>
            </>
          )}

        </div>
      )}

    </div>
  );
}


/* ================================================= */
/* STUDENT WALLET */
/* ================================================= */

function StudentWallet() {

  const [rollNumber, setRollNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const fetchCertificates = async () => {

    if (!rollNumber.trim()) {
      alert("Please enter your roll number.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/student/${encodeURIComponent(rollNumber)}/certificates`
      );

      const data = await response.json();
      setResult(data);

    } catch (error) {

      setResult({
        status: "error",
        message: "Could not connect to the backend. Make sure FastAPI is running.",
      });

    }

    setLoading(false);
  };

  return (
    <div className="card">

      <h2>Student Wallet</h2>

      <p className="description">
        Enter your roll number to view all your
        blockchain-verified certificates.
      </p>

      <form
        className="issue-form"
        onSubmit={(e) => {
          e.preventDefault();
          fetchCertificates();
        }}
      >

        <label>Roll Number</label>

        <input
          type="text"
          placeholder="e.g. 22-CS-107"
          value={rollNumber}
          onChange={(e) => setRollNumber(e.target.value)}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Loading Certificates..." : "View My Certificates"}
        </button>

      </form>

      {result && (
        <div className="result-card">

          {result.status === "error" ? (

            <p className="error">{result.message}</p>

          ) : result.total === 0 ? (

            <div className="coming-soon">
              <h3>No Certificates Found</h3>
              <p>
                No certificates are registered for roll number{" "}
                <strong>{result.roll_number}</strong>.
              </p>
            </div>

          ) : (

            <>
              <div className="status">
                {result.total} Certificate{result.total > 1 ? "s" : ""} Found
              </div>

              <div className="wallet-list">

                {result.certificates.map((cert, index) => (

                  <div key={index} className="wallet-card">

                    <div className="wallet-card-header">

                      <div className="wallet-card-icon">📄</div>

                      <div className="wallet-card-title">

                        <strong>
                          Certificate #{index + 1}
                        </strong>

                        <span>
                          {cert.issuer_name || "Unknown Issuer"}
                        </span>

                      </div>

                      <div className={
                        cert.status === "AUTHENTIC"
                          ? "wallet-status valid"
                          : "wallet-status revoked"
                      }>
                        {cert.status}
                      </div>

                    </div>

                    <div className="wallet-card-body">

                      <div className="wallet-field">
                        <span className="wallet-label">Document Hash</span>
                        <strong className="hash">{cert.doc_hash}</strong>
                      </div>

                      <div className="wallet-field">
                        <span className="wallet-label">Issued At</span>
                        <strong>
                          {new Date(cert.issued_at * 1000).toLocaleDateString()}
                        </strong>
                      </div>

                      <div className="wallet-field">
                        <span className="wallet-label">AI Risk Score</span>
                        <strong>{cert.ai_risk_score}</strong>
                      </div>

                      {cert.ipfs_cid && (
                        <div className="wallet-field">
                          <span className="wallet-label">IPFS CID</span>
                          <strong className="hash">{cert.ipfs_cid}</strong>
                        </div>
                      )}

                    </div>

                    <div className="wallet-card-footer" style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>

                      <a
                        href={cert.verification_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="wallet-btn"
                      >
                        Verify Certificate →
                      </a>

                      {cert.qr_pdf_url && (
                        <a
                          href={cert.qr_pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="wallet-btn"
                          style={{ background: "#059669" }}
                        >
                          📥 Download PDF
                        </a>
                      )}

                    </div>

                  </div>

                ))}

              </div>
            </>

          )}

        </div>
      )}

    </div>
  );
}


export default App;