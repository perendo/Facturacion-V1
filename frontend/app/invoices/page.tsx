"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import type { Invoice, Client } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import { Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";

const money = (n: number) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);

export default function InvoicesPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [clientId, setClientId] = useState("");
  const [status, setStatus] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [number, setNumber] = useState("");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Invoice[]>("/invoices", {
        client_id: clientId ? Number(clientId) : undefined,
        status: status || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        number: number || undefined,
      });
      setInvoices(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    apiGet<Client[]>("/clients").then(setClients).catch(() => {});
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Facturas</h1>
        <Button onClick={() => router.push("/invoices/new")}>Nueva factura</Button>
      </div>
      <Card>
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Select
            label="Cliente"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            options={[
              { value: "", label: "Todos" },
              ...clients.map((c) => ({ value: c.id, label: c.name })),
            ]}
          />
          <Select
            label="Estado"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            options={[
              { value: "", label: "Todos" },
              { value: "draft", label: "Borrador" },
              { value: "sent", label: "Enviada" },
              { value: "paid", label: "Pagada" },
              { value: "cancelled", label: "Cancelada" },
            ]}
          />
          <Input label="Desde" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          <Input label="Hasta" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          <Input label="Número" value={number} onChange={(e) => setNumber(e.target.value)} />
        </div>
        <div className="mb-4">
          <Button variant="secondary" onClick={load}>
            Filtrar
          </Button>
        </div>
        {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
        {loading ? (
          <p className="text-slate-500">Cargando...</p>
        ) : invoices.length === 0 ? (
          <p className="text-slate-500">Sin facturas.</p>
        ) : (
          <Table>
            <Thead>
              <Tr>
                <Th>Número</Th>
                <Th>Cliente</Th>
                <Th>Fecha</Th>
                <Th>Estado</Th>
                <Th>Total</Th>
              </Tr>
            </Thead>
            <Tbody>
              {invoices.map((inv) => {
                const client = clients.find((c) => c.id === inv.client_id);
                return (
                  <Tr key={inv.id}>
                    <Td>
                      <button
                        className="font-medium text-indigo-600 hover:underline"
                        onClick={() => router.push(`/invoices/${inv.id}`)}
                      >
                        {inv.number}
                      </button>
                    </Td>
                    <Td>{client?.name || inv.client_id || "-"}</Td>
                    <Td>{inv.issue_date}</Td>
                    <Td>
                      <Badge value={inv.status} />
                    </Td>
                    <Td>{money(inv.total)}</Td>
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        )}
      </Card>
    </div>
  );
}