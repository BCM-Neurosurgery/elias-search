import React from "react";
import { useNavigate } from "react-router"

export default function Login() {
    const navigate = useNavigate();

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault(),
        document.cookie = "auth=true; path:/";
        navigate("/dashboard");
    }

    return (
        <form onSubmit={handleLogin}>
            <input placeholder="Username" className="border p-2" />
            <input type="password" placeholder="Password" className="border p-2" />
            <button type="submit" className="bg-blue-600 text-white p-2 rounded">
                Login
            </button>
        </form>
    );
}