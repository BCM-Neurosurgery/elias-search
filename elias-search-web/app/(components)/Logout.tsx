"use client"
import { useRouter } from "next/navigation";

export default function Logout() {
    const router = useRouter();

    const handleLogout = async () => {
        await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/logout/`, {
            method: "POST",
            credentials: "include",
        });
        router.push("/login");
    };
    return (
    <button 
        onClick={handleLogout}
        className="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
    >
        Logout
    </button>
    );
}