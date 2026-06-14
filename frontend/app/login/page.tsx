"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Нэвтрэхэд алдаа гарлаа");
        return;
      }
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Сервертэй холбогдож чадсангүй");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 40, maxWidth: 400 }}>
      <h2>Нэвтрэх</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input
          placeholder="И-мэйл"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: 8, fontSize: 16 }}
        />
        <input
          placeholder="Нууц үг"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: 8, fontSize: 16 }}
          onKeyDown={(e) => e.key === "Enter" && handleLogin()}
        />
        {error && <p style={{ color: "red", margin: 0 }}>{error}</p>}
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{ padding: 10, fontSize: 16, cursor: "pointer" }}
        >
          {loading ? "Түр хүлээнэ үү..." : "Нэвтрэх"}
        </button>
      </div>
    </div>
  );
}
