"use client";
import { useEffect, useState } from "react";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import type { Product } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import { Table, Thead, Tbody, Tr, Th, Td } from "@/components/ui/Table";

const emptyForm = {
  name: "",
  description: "",
  unit_price: "",
  tax_rate: "21",
  unit: "",
};

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Product[]>("/products", { search: q ?? search });
      setProducts(data);
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

  const openEdit = (p: Product) => {
    setEditing(p);
    setForm({
      name: p.name,
      description: p.description || "",
      unit_price: String(p.unit_price),
      tax_rate: String(p.tax_rate),
      unit: p.unit || "",
    });
    setModalOpen(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        description: form.description || null,
        unit_price: Number(form.unit_price || 0),
        tax_rate: Number(form.tax_rate || 0),
        unit: form.unit || null,
      };
      if (editing) {
        await apiPut(`/products/${editing.id}`, payload);
      } else {
        await apiPost("/products", payload);
      }
      setModalOpen(false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: number) => {
    if (!confirm("¿Eliminar producto?")) return;
    try {
      await apiDelete(`/products/${id}`);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    }
  };

  const money = (n: number) =>
    new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Productos / Servicios</h1>
        <Button onClick={openCreate}>Nuevo producto</Button>
      </div>
      <Card>
        <div className="mb-4 flex gap-2">
          <Input
            placeholder="Buscar por nombre o descripción"
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
        ) : products.length === 0 ? (
          <p className="text-slate-500">Sin productos.</p>
        ) : (
          <Table>
            <Thead>
              <Tr>
                <Th>Nombre</Th>
                <Th>Precio</Th>
                <Th>IVA</Th>
                <Th>Unidad</Th>
                <Th>Acciones</Th>
              </Tr>
            </Thead>
            <Tbody>
              {products.map((p) => (
                <Tr key={p.id}>
                  <Td>
                    <div className="font-medium">{p.name}</div>
                    <div className="text-xs text-slate-500">{p.description}</div>
                  </Td>
                  <Td>{money(p.unit_price)}</Td>
                  <Td>{p.tax_rate}%</Td>
                  <Td>{p.unit}</Td>
                  <Td>
                    <div className="flex gap-2">
                      <Button variant="ghost" onClick={() => openEdit(p)}>
                        Editar
                      </Button>
                      <Button variant="danger" onClick={() => remove(p.id)}>
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

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Editar producto" : "Nuevo producto"}>
        <div className="flex flex-col gap-3">
          <Input label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label="Descripción" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Input label="Precio unitario" type="number" step="0.01" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} />
          <Input label="IVA (%)" type="number" step="0.01" value={form.tax_rate} onChange={(e) => setForm({ ...form, tax_rate: e.target.value })} />
          <Input label="Unidad" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
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
    </div>
  );
}