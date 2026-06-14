"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();
  const [protocols, setProtocols] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetch("http://localhost:8000/protocols/", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setProtocols(data))
      .catch(() => router.push("/login"));
  }, []);

  function handleLogout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <div style={{ padding: 40 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Судалгааны хүсэлтүүд</h1>
        <button onClick={handleLogout}>Гарах</button>
      </div>
      {protocols.length === 0 ? (
        <p>Одоогоор судалгааны хүсэлт байхгүй байна.</p>
      ) : (
        <ul>
          {protocols.map((p: any) => (
            <li key={p.id}>{p.title} — {p.status}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
