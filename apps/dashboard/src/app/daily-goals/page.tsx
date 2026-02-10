"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Flame,
  CheckCircle2,
  Circle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Header } from "@/components/header";
import { DashboardTabs } from "@/components/dashboard-tabs";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { useGetDailyGoalsToday } from "@/api/generated/daily-goals/daily-goals";
import { useGetDailyGoalsCalendar } from "@/api/generated/daily-goals/daily-goals";
import type { GoalProgress, DailyGoalDay } from "@/api/generated/model";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function toDateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function monthRange(year: number, month: number) {
  const from = new Date(year, month, 1);
  const to = new Date(year, month + 1, 0);
  return { from: toDateString(from), to: toDateString(to) };
}

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function GoalProgressBar({ goal }: { goal: GoalProgress }) {
  const pct =
    goal.target > 0
      ? Math.min(100, Math.round((goal.current / goal.target) * 100))
      : 0;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">{goal.label}</span>
        <span className="text-muted-foreground tabular-nums">
          {goal.current}/{goal.target}
        </span>
      </div>
      <div className="h-2 rounded-full bg-warm-200 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            goal.achieved ? "bg-emerald-500" : "bg-terra-light"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function CalendarGrid({
  year,
  month,
  items,
}: {
  year: number;
  month: number;
  items: DailyGoalDay[];
}) {
  const today = toDateString(new Date());

  const lookup = useMemo(() => {
    const map = new Map<string, boolean>();
    for (const item of items) {
      map.set(item.date, item.achieved);
    }
    return map;
  }, [items]);

  const firstDay = new Date(year, month, 1);
  const startOffset = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const cells: { day: number | null; dateStr: string | null }[] = [];
  for (let i = 0; i < startOffset; i++)
    cells.push({ day: null, dateStr: null });
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, dateStr: toDateString(new Date(year, month, d)) });
  }

  return (
    <div>
      <div className="grid grid-cols-7 gap-1 mb-1">
        {WEEKDAYS.map((wd) => (
          <div
            key={wd}
            className="text-center text-[11px] font-medium text-muted-foreground py-1"
          >
            {wd}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {cells.map((cell, idx) => {
          if (cell.day === null) {
            return <div key={`empty-${idx}`} />;
          }
          const achieved = cell.dateStr ? lookup.get(cell.dateStr) : undefined;
          const isToday = cell.dateStr === today;

          let bg = "bg-warm-100";
          if (achieved === true) bg = "bg-emerald-100 text-emerald-800";
          if (achieved === false) bg = "bg-red-100 text-red-700";

          return (
            <div
              key={cell.dateStr}
              className={`relative flex items-center justify-center rounded-lg h-9 text-xs font-medium transition-colors ${bg} ${
                isToday ? "ring-2 ring-primary ring-offset-1 ring-offset-background" : ""
              }`}
            >
              {cell.day}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DailyGoalsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [calYear, setCalYear] = useState(() => new Date().getFullYear());
  const [calMonth, setCalMonth] = useState(() => new Date().getMonth());

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const { data: todayData, isLoading: isTodayLoading } =
    useGetDailyGoalsToday({
      query: { enabled: isAuthenticated },
    });

  const { from, to } = monthRange(calYear, calMonth);
  const { data: calendarData, isLoading: isCalendarLoading } =
    useGetDailyGoalsCalendar(
      { from, to },
      { query: { enabled: isAuthenticated } },
    );

  const todayGoal = todayData?.data;
  const calendarItems = calendarData?.data?.items ?? [];

  function prevMonth() {
    setCalMonth((m) => {
      if (m === 0) {
        setCalYear((y) => y - 1);
        return 11;
      }
      return m - 1;
    });
  }

  function nextMonth() {
    setCalMonth((m) => {
      if (m === 11) {
        setCalYear((y) => y + 1);
        return 0;
      }
      return m + 1;
    });
  }

  const monthLabel = new Date(calYear, calMonth).toLocaleString("default", {
    month: "long",
    year: "numeric",
  });

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <DashboardTabs />

      <main className="px-6 py-8 max-w-3xl mx-auto space-y-6">
        {/* ---- Today card ---- */}
        <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-foreground mb-4">Today</h2>

          {isTodayLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : !todayGoal ? (
            <p className="text-sm text-muted-foreground">
              No goal data for today.
            </p>
          ) : (
            <div className="space-y-5">
              {/* Status + streak */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {todayGoal.achieved ? (
                    <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                  ) : (
                    <Circle className="h-6 w-6 text-warm-300" />
                  )}
                  <div>
                    <p className="font-medium text-foreground">
                      {todayGoal.achieved
                        ? "All goals achieved!"
                        : "Goals in progress"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {todayGoal.date}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200">
                  <Flame className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-medium text-amber-700 tabular-nums">
                    {todayGoal.streak}
                  </span>
                </div>
              </div>

              {/* Per-goal progress */}
              {todayGoal.goals.length > 0 && (
                <div className="space-y-3">
                  {todayGoal.goals.map((goal: GoalProgress) => (
                    <GoalProgressBar key={goal.goal_type} goal={goal} />
                  ))}
                </div>
              )}
            </div>
          )}
        </section>

        {/* ---- Calendar card ---- */}
        <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-foreground">Calendar</h2>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                onClick={prevMonth}
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm font-medium text-foreground min-w-[140px] text-center">
                {monthLabel}
              </span>
              <Button
                variant="ghost"
                size="icon"
                onClick={nextMonth}
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {isCalendarLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : (
            <>
              <CalendarGrid
                year={calYear}
                month={calMonth}
                items={calendarItems}
              />

              <div className="flex items-center gap-5 mt-5 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded bg-emerald-100 border border-emerald-200" />
                  <span>Achieved</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded bg-red-100 border border-red-200" />
                  <span>Missed</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded bg-warm-100 border border-warm-200" />
                  <span>No data</span>
                </div>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
