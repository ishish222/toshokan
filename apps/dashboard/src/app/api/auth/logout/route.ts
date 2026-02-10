import { redirect } from "next/navigation";
import { getLogoutUrl } from "@/lib/auth";

export async function GET() {
    redirect(getLogoutUrl());
}
