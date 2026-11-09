"use client";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";
import Card from "@/components/ui/Card";
import { Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui/Table";

const money = (n: number) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<DashboardSummary>("/dashboard/summary")
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Error"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-500">Cargando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!data) return null;

  const counts = data.count_by_status || {};

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Total facturado">
          <p className="text-2xl font-bold text-indigo-600">{money(data.total_invoiced)}</p>
        </Card>
        <Card title="Cobrado">
          <p className="text-2xl font-bold text-green-600">{money(data.total_paid)}</p>
        </Card>
        <Card title="Pendiente">
          <p className="text-2xl font-bold text-amber-600">{money(data.total_pending)}</p>
        </Card>
        <Card title="Facturas">
          <p className="text-2xl font-bold text-slate-700">
            {Object.values(counts).reduce((a, b) => a + b, 0)}
          </p>
        </Card>
      </div>
      <Card title="Conteo por estado">
        <Table>
          <Thead>
            <Tr>
              <Th>Estado</Th>
              <Th>Cantidad</Th>
            </Tr>
          </Thead>
          <Tbody>
            {["draft", "sent", "paid", "cancelled"].map((s) => (
              <Tr key={s}>
                <Td>
                  <span className="capitalize">{s}</span>
                </Td>
                <Td>{counts[s] ?? 0}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Card>
    </div>
  );
}