"use client";
import { Suspense, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiGet, apiPatch, apiDelete } from "@/lib/api";
import type { Invoice, Client } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";
import { Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui/Table";
import InvoiceForm from "@/components/invoices/InvoiceForm";

const money = (n: number) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);

const transitions: Record<string, string[]> = {
  draft: ["sent", "cancelled"],
  sent: ["paid", "cancelled"],
  paid: [],
  cancelled: [],
};

function InvoiceDetailInner() {
  const params = useParams();
  const id = Number(params.id);
  const router = useRouter();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [changing, setChanging] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const inv = await apiGet<Invoice>(`/invoices/${id}`);
      setInvoice(inv);
      if (inv.client_id) {
        try {
          const c = await apiGet<Client>(`/clients/${inv.client_id}`);
          setClient(c);
        } catch {
          setClient(null);
        }
      } else {
        setClient(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const changeStatus = async (status: string) => {
    setChanging(true);
    try {
      await apiPatch(`/invoices/${id}/status`, { status });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setChanging(false);
    }
  };

  const remove = () => setConfirmDelete(true);

  const doDelete = async () => {
    try {
      await apiDelete(`/invoices/${id}`);
      router.push("/invoices");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setConfirmDelete(false);
    }
  };

  const downloadPdf = async () => {
    setDownloading(true);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_BASE}/api/v1/invoices/${id}/pdf`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("No se pudo generar el PDF");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${invoice?.number || "factura"}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return <p className="text-slate-500">Cargando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!invoice) return null;

  if (editing) {
    return (
      <div>
        <Button variant="secondary" onClick={() => setEditing(false)} className="mb-4">
          Volver
        </Button>
        <InvoiceForm mode="edit" invoiceId={id} initial={invoice} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">{invoice.number}</h1>
          <Badge value={invoice.status} />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" loading={downloading} onClick={downloadPdf}>
            Descargar PDF
          </Button>
          {transitions[invoice.status]?.map((s) => (
            <Button key={s} loading={changing} onClick={() => changeStatus(s)}>
              {s === "sent" ? "Marcar enviada" : s === "paid" ? "Marcar pagada" : s === "cancelled" ? "Cancelar" : s}
            </Button>
          ))}
          {invoice.status === "draft" && (
            <>
              <Button variant="secondary" onClick={() => setEditing(true)}>
                Editar
              </Button>
              <Button variant="danger" onClick={remove}>
                Eliminar
              </Button>
            </>
          )}
        </div>
      </div>

      <Card>
        <div className="grid gap-3 sm:grid-cols-2">
          <p><span className="font-medium">Cliente:</span> {client?.name || invoice.client_id || "-"}</p>
          <p><span className="font-medium">Fecha emisión:</span> {invoice.issue_date}</p>
          <p><span className="font-medium">Vencimiento:</span> {invoice.due_date || "-"}</p>
          <p><span className="font-medium">Descuento global:</span> {invoice.global_discount}%</p>
          <p className="sm:col-span-2"><span className="font-medium">Notas:</span> {invoice.notes || "-"}</p>
        </div>
      </Card>

      <Card title="Líneas">
        <Table>
          <Thead>
            <Tr>
              <Th>Descripción</Th>
              <Th>Cantidad</Th>
              <Th>Precio</Th>
              <Th>Desc. %</Th>
              <Th>IVA %</Th>
              <Th>Subtotal</Th>
              <Th>IVA</Th>
              <Th>Total</Th>
            </Tr>
          </Thead>
          <Tbody>
            {invoice.lines.map((l) => (
              <Tr key={l.id}>
                <Td>{l.description}</Td>
                <Td>{l.quantity}</Td>
                <Td>{money(l.unit_price)}</Td>
                <Td>{l.discount}</Td>
                <Td>{l.tax_rate}</Td>
                <Td>{money(l.line_subtotal)}</Td>
                <Td>{money(l.line_tax)}</Td>
                <Td>{money(l.line_total)}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
        <div className="mt-4 flex justify-end">
          <div className="w-64 rounded-lg bg-slate-50 p-3 text-sm">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{money(invoice.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>IVA</span>
              <span>{money(invoice.tax_total)}</span>
            </div>
            <div className="mt-1 flex justify-between border-t border-slate-200 pt-1 font-semibold">
              <span>Total</span>
              <span>{money(invoice.total)}</span>
            </div>
          </div>
        </div>
      </Card>

      <Modal open={confirmDelete} onClose={() => setConfirmDelete(false)} title="Confirmar eliminación">
        <p className="text-sm text-slate-600">¿Eliminar factura?</p>
        <div className="flex justify-end gap-2 pt-3">
          <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={doDelete}>
            Eliminar
          </Button>
        </div>
      </Modal>
    </div>
  );
}

export default function InvoiceDetailPage() {
  return (
    <Suspense fallback={<p className="text-slate-500">Cargando...</p>}>
      <InvoiceDetailInner />
    </Suspense>
  );
}