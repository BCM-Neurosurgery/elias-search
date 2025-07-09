import Link from "next/link";
import { redirect } from "next/navigation";

export default function Home() {
  // always redirect to login
  redirect("/login");
  return (
    <div>dummy page - please go to <Link href="/login">Login</Link></div>
  );
}
