import { useEffect, useState } from "react";
import { useNavigate } from "react-router"
import QueryForm from "../components/QueryForm/QueryForm";
import QueryResponse from '../components/QueryResponse';

export default function Dashboard() {
    // set hooks
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [queryResult, setQueryResult] = useState<any | null>(null);
    const [queryPayload, setQueryPayload] = useState<any | null>(null);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/status/`, {
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
        <div className="p-6 space-y-6">
            <QueryForm
                onResult={(data) => {
                    setQueryPayload(data.query);
                    setQueryResult(data.result);
                }}
            />
            {queryResult && (
                <QueryResponse
                    result={queryResult}
                    payload={queryPayload} 
                />
            )}
        </div>
    )
}
