import React, { useState } from "react";
import { useNavigate } from "react-router"

export default function Login() {
    // set hooks
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch("http://elias.bcms.bcm.edu/api/auth/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password}),
                credentials: "include",
            });

            const data = await response.json();
            if (data.success) {
                navigate("/dashboard");
            } else {
                alert("Login failed: " + (data.error || "Unknown error"));
            }
        } catch (err) {
            alert("Network or server error");
        }
    }

    return (
        <form onSubmit={handleLogin}>
            <input 
                placeholder="Username" 
                className="border p-2" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input 
                type="password" 
                placeholder="Password" 
                className="border p-2" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit" className="bg-blue-600 text-white p-2 rounded">
                Login
            </button>
        </form>
    );
}