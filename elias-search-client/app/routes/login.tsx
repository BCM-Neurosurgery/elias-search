import React, { useState } from "react";
import { useNavigate } from "react-router";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/login/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
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
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
            <form
                onSubmit={handleLogin}
                className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-md w-full max-w-sm border border-gray-300 dark:border-gray-700"
            >
                <h2 className="text-2xl font-semibold mb-6 text-center text-gray-800 dark:text-gray-100">
                    Log In
                </h2>

                <div className="mb-4">
                    <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                        Username
                    </label>
                    <input
                        type="text"
                        placeholder="Enter username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        required
                    />
                </div>

                <div className="mb-6">
                    <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                        Password
                    </label>
                    <input
                        type="password"
                        placeholder="Enter password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        required
                    />
                </div>

                <button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md transition duration-200"
                >
                    Login
                </button>
            </form>
        </div>
    );
}
