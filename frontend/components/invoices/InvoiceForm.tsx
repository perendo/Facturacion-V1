"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiPut } from "@/lib/api";
import type { Client, Product, Invoice, InvoiceLineCreate } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Textarea from "@/components/ui/Textarea";

interface LineState {
  product_id: number | null;
  description: string;
  quantity: string;
  unit_price: string;
  discount: string;
  tax_rate: string;
}

const emptyLine: LineState = {
  product_id: null,
  description: "",
  quantity: "1",
  unit_price: "0",
  discount: "0",
  tax_rate: "21",
};

interface Props {
  mode: "create" | "edit";
  invoiceId?: number;
  initial?: Invoice;
}

function toNumber(v: string): number {
  const n = Number(v);
  return isNaN(n) ? 0 : n;
}

function calcTotals(lines: LineState[], globalDiscount: number) {
  let subtotal = 0;
  let tax = 0;
  lines.forEach((l) => {
    const qty = toNumber(l.quantity);
    const price = toNumber(l.unit_price);
    const disc = toNumber(l.discount);
    const taxRate = toNumber(l.tax_rate);
    const base = qty * price * (1 - disc / 100);
    subtotal += base;
    tax += base * (taxRate / 100);
  });
  const discountedSubtotal = subtotal * (1 - globalDiscount / 100);
  const discountedTax = tax * (1 - globalDiscount / 100);
  return {
    subtotal: discountedSubtotal,
    tax: discountedTax,
    total: discountedSubtotal + discountedTax,
  };
}

export default function InvoiceForm({ mode, invoiceId, initial }: Props) {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [clientId, setClientId] = useState<string>(initial?.client_id ? String(initial.client_id) : "");
  const [issueDate, setIssueDate] = useState<string>(initial?.issue_date || "");
  const [dueDate, setDueDate] = useState<string>(initial?.due_date || "");
  const [globalDiscount, setGlobalDiscount] = useState<string>(String(initial?.global_discount ?? 0));
  const [notes, setNotes] = useState<string>(initial?.notes || "");
  const [lines, setLines] = useState<LineState[]>(
    initial?.lines?.length
      ? initial.lines.map((l) => ({
          product_id: l.product_id,
          description: l.description,
          quantity: String(l.quantity),
          unit_price: String(l.unit_price),
          discount: String(l.discount),
          tax_rate: String(l.tax_rate),
        }))
      : [emptyLine]
  );
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Client[]>("/clients").then(setClients).catch(() => {});
    apiGet<Product[]>("/products").then(setProducts).catch(() => {});
  }, []);

  useEffect(() => {
    if (!initial?.issue_date && !issueDate) {
      setIssueDate(new Date().toISOString().slice(0, 10));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addLineFromProduct = () => {
    const p = products.find((x) => x.id === Number(selectedProduct));
    if (!p) return;
    setLines((prev) => [
      ...prev,
      {
        product_id: p.id,
        description: p.name,
        quantity: "1",
        unit_price: String(p.unit_price),
        discount: "0",
        tax_rate: String(p.tax_rate),
      },
    ]);
    setSelectedProduct("");
  };

  const addEmptyLine = () => setLines((prev) => [...prev, { ...emptyLine }]);

  const updateLine = (idx: number, patch: Partial<LineState>) => {
    setLines((prev) => prev.map((l, i) => (i === idx ? { ...l, ...patch } : l)));
  };

  const removeLine = (idx: number) => {
    setLines((prev) => prev.filter((_, i) => i !== idx));
  };

  const totals = calcTotals(lines, toNumber(globalDiscount));

  const submit = async () => {
    setError(null);
    if (lines.length === 0) {
      setError("Añade al menos una línea");
      return;
    }
    setSaving(true);
    try {
      const payloadLines: InvoiceLineCreate[] = lines.map((l) => ({
        product_id: l.product_id,
        description: l.description || "Línea",
        quantity: toNumber(l.quantity),
        unit_price: toNumber(l.unit_price),
        discount: toNumber(l.discount),
        tax_rate: toNumber(l.tax_rate),
      }));
      const payload = {
        client_id: clientId ? Number(clientId) : null,
        issue_date: issueDate,
        due_date: dueDate || null,
        global_discount: toNumber(globalDiscount),
        notes: notes || null,
        lines: payloadLines,
      };
      let saved: Invoice;
      if (mode === "create") {
        saved = await apiPost<Invoice>("/invoices", payload);
      } else {
        saved = await apiPut<Invoice>(`/invoices/${invoiceId}`, payload);
      }
      router.push(`/invoices/${saved.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  const money = (n: number) =>
    new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-slate-800">
        {mode === "create" ? "Nueva factura" : "Editar factura"}
      </h1>
      <Card>
        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Cliente"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            options={[
              { value: "", label: "Sin cliente" },
              ...clients.map((c) => ({ value: c.id, label: c.name })),
            ]}
          />
          <Input label="Fecha emisión" type="date" value={issueDate} onChange={(e) => setIssueDate(e.target.value)} />
          <Input label="Fecha vencimiento" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          <Input label="Descuento global (%)" type="number" step="0.01" value={globalDiscount} onChange={(e) => setGlobalDiscount(e.target.value)} />
        </div>
        <div className="mt-4">
          <Textarea label="Notas" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
        </div>
      </Card>

      <Card title="Líneas">
        <div className="mb-4 flex flex-wrap items-end gap-2">
          <div className="flex-1 min-w-[200px]">
            <Select
              label="Añadir producto"
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              options={[
                { value: "", label: "Seleccionar..." },
                ...products.map((p) => ({ value: p.id, label: `${p.name} (${p.unit_price})` })),
              ]}
            />
          </div>
          <Button variant="secondary" onClick={addLineFromProduct} disabled={!selectedProduct}>
            Añadir
          </Button>
          <Button variant="ghost" onClick={addEmptyLine}>
            Línea manual
          </Button>
        </div>

        <div className="flex flex-col gap-3">
          {lines.map((line, idx) => (
            <div key={idx} className="rounded-lg border border-slate-200 p-3">
              <div className="grid gap-2 sm:grid-cols-6">
                <div className="sm:col-span-2">
                  <Input
                    label="Descripción"
                    value={line.description}
                    onChange={(e) => updateLine(idx, { description: e.target.value })}
                  />
                </div>
                <Input
                  label="Cantidad"
                  type="number"
                  step="0.01"
                  value={line.quantity}
                  onChange={(e) => updateLine(idx, { quantity: e.target.value })}
                />
                <Input
                  label="Precio"
                  type="number"
                  step="0.01"
                  value={line.unit_price}
                  onChange={(e) => updateLine(idx, { unit_price: e.target.value })}
                />
                <Input
                  label="Desc. %"
                  type="number"
                  step="0.01"
                  value={line.discount}
                  onChange={(e) => updateLine(idx, { discount: e.target.value })}
                />
                <Input
                  label="IVA %"
                  type="number"
                  step="0.01"
                  value={line.tax_rate}
                  onChange={(e) => updateLine(idx, { tax_rate: e.target.value })}
                />
              </div>
              <div className="mt-2 flex justify-end">
                <Button variant="danger" onClick={() => removeLine(idx)}>
                  Eliminar línea
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex justify-end">
          <div className="w-64 rounded-lg bg-slate-50 p-3 text-sm">
            <div className="flex justify-between">
              <span>Subtotal</span>
              <span>{money(totals.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>IVA</span>
              <span>{money(totals.tax)}</span>
            </div>
            <div className="mt-1 flex justify-between border-t border-slate-200 pt-1 font-semibold">
              <span>Total</span>
              <span>{money(totals.total)}</span>
            </div>
          </div>
        </div>
      </Card>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={() => router.push("/invoices")}>
          Cancelar
        </Button>
        <Button loading={saving} onClick={submit}>
          {mode === "create" ? "Crear factura" : "Guardar cambios"}
        </Button>
      </div>
    </div>
  );
}