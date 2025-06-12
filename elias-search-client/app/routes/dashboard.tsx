import { useEffect, useState } from "react";
import { useNavigate } from "react-router"

export default function Dashboard() {
    // set hooks
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await fetch("http://elias.bcms.bcm.edu/api/auth/status/", {
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
            <h1 className="text-x1 p-4">Streamlit Dashboard</h1>
        </div>
    )
}
