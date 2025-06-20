import { useEffect, useState } from "react";
import { useNavigate } from "react-router"
import QueryForm from "../components/QueryForm/QueryForm";

export default function Dashboard() {
    // set hooks
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await fetch("/api/auth/status/", {
                    credentials: "include",
                });
                const data = await response.json();
                if (!data.authenticated) {
                    navigate("/login");
                } else {
                    setLoading(false);
                }
            } catch (err) {
                console.error("Error checking auth status", err);
                navigate("/login");
            }
        };
        
        checkAuth();
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>
    }
    
    return (
        <div className="h-screen">
            <h1 className="text-x1 p-4">Dashboard</h1>
            <QueryForm/>
        </div>
    )
}
