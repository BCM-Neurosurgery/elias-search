"use client"
import { useEffect } from 'react'
import { useRouter } from "next/navigation";
import Login from './Login';

export default function LoginPage() {
    // check if already authenticated
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
                if (data.authenticated) {
                    router.push("/dashboard");
                }
            } catch (err) {
                console.log(err);
            }
         })();
     }, []) 
    return <Login />
}
