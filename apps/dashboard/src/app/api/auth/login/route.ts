import { redirect } from "next/navigation";
import { getLoginUrl } from "@/lib/auth";

export async function GET() {
    redirect(getLoginUrl());
}
