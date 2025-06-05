export default function Dashboard() {
    const isAuth = document.cookie.includes("auth=true");
    if (!isAuth) {
        window.location.href = "/login";
        return null;
    }
    
    return (
        <div className="h-screen">
            <h1 className="text-x1 p-4">Streamlit Dashboard</h1>
            <iframe
                src="http://elias.bcms.bcm.edu/streamlit"
                className="w-full h-[80vh] border"
                title="Streamlit UI"
            />
        </div>
    )
}

