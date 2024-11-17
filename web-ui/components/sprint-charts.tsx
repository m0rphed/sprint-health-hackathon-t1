"use client";

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { cn } from '@/lib/utils';
import sprintData from '@/lib/data/sprint-stats.json';

const COLORS = {
  done: 'hsl(var(--chart-1))',
  backlogged: 'hsl(var(--chart-2))',
  removed: 'hsl(var(--chart-3))',
  inProgress: 'hsl(var(--chart-4))',
  estimate: 'hsl(var(--chart-5))',
};

interface SprintChartsProps {
  sprintId?: string;
}

export function SprintCharts({ sprintId }: SprintChartsProps) {
  // Transform assignee data for the estimation vs spent chart
  const assigneeData = sprintData.assignees.map(({ assignee, estimation, spent }) => ({
    name: assignee,
    estimation,
    spent,
  }));

  // Transform data for task status pie chart
  const taskStatusData = [
    { name: 'Done', value: sprintData.taskStatus.done },
    { name: 'Backlogged', value: sprintData.taskStatus.backlogged },
    { name: 'Removed', value: sprintData.taskStatus.removed },
    {
      name: 'In Progress',
      value: sprintData.taskStatus.total - (
        sprintData.taskStatus.done +
        sprintData.taskStatus.backlogged +
        sprintData.taskStatus.removed
      ),
    },
  ];

  // Transform daily changes data
  const dailyChangesData = Object.entries(sprintData.dailyChanges).map(([day, changes]) => ({
    day: `Day ${day}`,
    added: changes.added,
    removed: changes.removed,
  }));

  const getPercentageColorClass = (percent: number) => {
    const absPercent = Math.abs(percent);
    if (absPercent <= 10) return 'bg-green-500/10 hover:bg-green-500/20';
    if (absPercent <= 20) return 'bg-yellow-500/10 hover:bg-yellow-500/20';
    if (absPercent <= 60) return 'bg-red-500/10 hover:bg-red-500/20';
    return '';
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Sprint Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">Total Tasks</p>
            <p className="text-2xl font-bold">{sprintData.taskStatus.total}</p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">Completion Rate</p>
            <p className="text-2xl font-bold">
              {Math.round((sprintData.taskStatus.done / sprintData.taskStatus.total) * 100)}%
            </p>
          </div>
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">Total Story Points</p>
            <p className="text-2xl font-bold">
              {sprintData.assignees.reduce((sum, a) => sum + a.estimation, 0)}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[300px]">
            <h4 className="text-sm font-medium mb-4">Task Status Distribution</h4>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={taskStatusData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {taskStatusData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={Object.values(COLORS)[index % Object.values(COLORS).length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="h-[300px]">
            <h4 className="text-sm font-medium mb-4">Daily Task Changes</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dailyChangesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="added" name="Added" fill={COLORS.done} />
                <Bar dataKey="removed" name="Removed" fill={COLORS.removed} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Estimation vs Spent Time by Assignee</h3>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={assigneeData} layout="vertical" margin={{ left: 50 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={60} />
              <Tooltip />
              <Legend />
              <Bar dataKey="estimation" name="Estimated" fill={COLORS.estimate} />
              <Bar dataKey="spent" name="Spent" fill={COLORS.done} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Sprint Performance Details</h3>
        <div className="relative overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Assignee</TableHead>
                <TableHead className="text-right">Estimation</TableHead>
                <TableHead className="text-right">Spent</TableHead>
                <TableHead className="text-right">Deviation (%)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sprintData.assignees.map((assignee) => (
                <TableRow key={assignee.assignee}>
                  <TableCell className="font-medium">{assignee.assignee}</TableCell>
                  <TableCell className="text-right">{assignee.estimation}</TableCell>
                  <TableCell className="text-right">{assignee.spent}</TableCell>
                  <TableCell className={cn(
                    "text-right rounded-md transition-colors",
                    getPercentageColorClass(assignee.procent)
                  )}>
                    {assignee.procent.toFixed(1)}%
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </div>
  );
}