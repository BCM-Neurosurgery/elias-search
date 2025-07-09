"use client"
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Dashboard from './Dashboard';

export default function DashboardPage() {
    // set up router
    const router = useRouter();
    // secheck auth
    useEffect(() => {
        (async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/status/`, 
                {
                    credentials: "include",
                }
                );
                const data = await res.json();
                if (!data.authenticated) {
                    router.push("/login");
                }
            } catch (err) {
                console.log(err);
                router.push("/login");
            }
        })();
    }, []) 
    return <Dashboard />
}
