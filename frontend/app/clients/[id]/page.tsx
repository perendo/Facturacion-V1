"use client";
import { Suspense, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiGet, apiPut, apiDelete } from "@/lib/api";
import type { Client } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

function ClientDetailInner() {
  const params = useParams();
  const id = Number(params.id);
  const router = useRouter();
  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    address: "",
    tax_id: "",
    notes: "",
  });

  const load = async () => {
    setLoading(true);
    try {
      const c = await apiGet<Client>(`/clients/${id}`);
      setClient(c);
      setForm({
        name: c.name,
        email: c.email || "",
        phone: c.phone || "",
        address: c.address || "",
        tax_id: c.tax_id || "",
        notes: c.notes || "",
      });
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

  const save = async () => {
    try {
      await apiPut(`/clients/${id}`, {
        name: form.name,
        email: form.email || null,
        phone: form.phone || null,
        address: form.address || null,
        tax_id: form.tax_id || null,
        notes: form.notes || null,
      });
      setEditing(false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    }
  };

  const remove = async () => {
    if (!confirm("¿Eliminar cliente?")) return;
    try {
      await apiDelete(`/clients/${id}`);
      router.push("/clients");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    }
  };

  if (loading) return <p className="text-slate-500">Cargando...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!client) return null;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">{client.name}</h1>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setEditing((v) => !v)}>
            {editing ? "Cancelar" : "Editar"}
          </Button>
          <Button variant="danger" onClick={remove}>
            Eliminar
          </Button>
        </div>
      </div>
      <Card>
        {!editing ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <p><span className="font-medium">Email:</span> {client.email || "-"}</p>
            <p><span className="font-medium">Teléfono:</span> {client.phone || "-"}</p>
            <p><span className="font-medium">Dirección:</span> {client.address || "-"}</p>
            <p><span className="font-medium">NIF/CIF:</span> {client.tax_id || "-"}</p>
            <p className="sm:col-span-2"><span className="font-medium">Notas:</span> {client.notes || "-"}</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <Input label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <Input label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <Input label="Teléfono" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Input label="Dirección" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            <Input label="NIF/CIF" value={form.tax_id} onChange={(e) => setForm({ ...form, tax_id: e.target.value })} />
            <Input label="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            <div className="flex justify-end">
              <Button onClick={save}>Guardar</Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

export default function ClientDetailPage() {
  return (
    <Suspense fallback={<p className="text-slate-500">Cargando...</p>}>
      <ClientDetailInner />
    </Suspense>
  );
}