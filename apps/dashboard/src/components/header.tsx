"use client";

import { LogOut, User, Coins } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { useGetMe } from "@/api/generated/user/user";
import { useGetCustomerTokens } from "@/api/generated/customer/customer";

export function Header() {
    const { logout, isAuthenticated } = useAuth();
    const { data: userData } = useGetMe({
        query: { enabled: isAuthenticated },
    });
    const { data: tokensData } = useGetCustomerTokens({
        query: { enabled: isAuthenticated },
    });

    const userEmail = userData?.data?.email ?? "Loading...";
    const tokenCount = tokensData?.data?.tokens ?? 0;

    return (
        <header className="bg-slate-900 border-b border-slate-800">
            <div className="flex items-center justify-between px-6 py-3">
                {/* Logo */}
                <div className="flex flex-col">
                    <span className="text-xl font-bold tracking-wider text-cyan-400">
                        NAVIGATOR
                    </span>
                    <span className="text-[10px] text-slate-500 -mt-1">by SEDIVIO</span>
                </div>

                {/* Right side - User info */}
                <div className="flex items-center gap-4">
                    {/* User email */}
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-700 bg-slate-800/50">
                        <User className="h-4 w-4 text-slate-400" />
                        <span className="text-sm text-slate-300">{userEmail}</span>
                    </div>

                    {/* Token count */}
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-700 bg-slate-800/50">
                        <Coins className="h-4 w-4 text-amber-400" />
                        <span className="text-sm text-slate-300 font-medium">
                            {tokenCount.toLocaleString()}
                        </span>
                    </div>

                    {/* Add tokens button */}
                    <Button
                        variant="outline"
                        size="sm"
                        className="border-cyan-600 text-cyan-400 hover:bg-cyan-600/10"
                    >
                        Add tokens
                    </Button>

                    {/* Logout button */}
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={logout}
                        className="text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                    >
                        <LogOut className="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </header>
    );
}
