"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import type { Client } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import { Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui/Table";


const emptyForm = {
  name: "",
  email: "",
  phone: "",
  address: "",
  tax_id: "",
  notes: "",
};

export default function ClientsPage() {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Client | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [toDelete, setToDelete] = useState<number | null>(null);

  const load = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Client[]>("/clients", { search: q ?? search });
      setClients(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (c: Client) => {
    setEditing(c);
    setForm({
      name: c.name,
      email: c.email || "",
      phone: c.phone || "",
      address: c.address || "",
      tax_id: c.tax_id || "",
      notes: c.notes || "",
    });
    setModalOpen(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        email: form.email || null,
        phone: form.phone || null,
        address: form.address || null,
        tax_id: form.tax_id || null,
        notes: form.notes || null,
      };
      if (editing) {
        await apiPut(`/clients/${editing.id}`, payload);
      } else {
        await apiPost("/clients", payload);
      }
      setModalOpen(false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  const remove = (id: number) => setToDelete(id);

  const confirmDelete = async () => {
    if (toDelete === null) return;
    try {
      await apiDelete(`/clients/${toDelete}`);
      setToDelete(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
      setToDelete(null);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Clientes</h1>
        <Button onClick={openCreate}>Nuevo cliente</Button>
      </div>
      <Card>
        <div className="mb-4 flex gap-2">
          <Input
            placeholder="Buscar por nombre o email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1"
          />
          <Button variant="secondary" onClick={() => load(search)}>
            Buscar
          </Button>
        </div>
        {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
        {loading ? (
          <p className="text-slate-500">Cargando...</p>
        ) : clients.length === 0 ? (
          <p className="text-slate-500">Sin clientes.</p>
        ) : (
          <Table>
            <Thead>
              <Tr>
                <Th>Nombre</Th>
                <Th>Email</Th>
                <Th>Teléfono</Th>
                <Th>NIF/CIF</Th>
                <Th>Acciones</Th>
              </Tr>
            </Thead>
            <Tbody>
              {clients.map((c) => (
                <Tr key={c.id}>
                  <Td>
                    <button
                      className="font-medium text-indigo-600 hover:underline"
                      onClick={() => router.push(`/clients/${c.id}`)}
                    >
                      {c.name}
                    </button>
                  </Td>
                  <Td>{c.email}</Td>
                  <Td>{c.phone}</Td>
                  <Td>{c.tax_id}</Td>
                  <Td>
                    <div className="flex gap-2">
                      <Button variant="ghost" onClick={() => openEdit(c)}>
                        Editar
                      </Button>
                      <Button variant="danger" onClick={() => remove(c.id)}>
                        Eliminar
                      </Button>
                    </div>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Editar cliente" : "Nuevo cliente"}>
        <div className="flex flex-col gap-3">
          <Input label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input label="Teléfono" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <Input label="Dirección" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
          <Input label="NIF/CIF" value={form.tax_id} onChange={(e) => setForm({ ...form, tax_id: e.target.value })} />
          <Input label="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancelar
            </Button>
            <Button loading={saving} onClick={save}>
              Guardar
            </Button>
          </div>
        </div>
      </Modal>

      <Modal open={toDelete !== null} onClose={() => setToDelete(null)} title="Confirmar eliminación">
        <p className="text-sm text-slate-600">¿Eliminar cliente?</p>
        <div className="flex justify-end gap-2 pt-3">
          <Button variant="secondary" onClick={() => setToDelete(null)}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={confirmDelete}>
            Eliminar
          </Button>
        </div>
      </Modal>
    </div>
  );
}