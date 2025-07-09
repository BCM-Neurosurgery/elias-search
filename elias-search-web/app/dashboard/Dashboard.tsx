"use client"
import { useState } from "react";
import QueryForm from "@/app/(components)/QueryForm/QueryForm";
import QueryResponse from '@/app/(components)/QueryResponse';
import Logout from '@/app/(components)/Logout';

export default function Dashboard() {
    // set hooks
    const [queryResult, setQueryResult] = useState<any | null>(null);
    const [queryPayload, setQueryPayload] = useState<any | null>(null);

    return (
        <div className="p-6 space-y-6">
            <Logout/>
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
