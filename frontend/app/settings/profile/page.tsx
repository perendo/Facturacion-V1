"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPut } from "@/lib/api";
import type { CompanyProfile, CompanyProfileCreate } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

export default function ProfilePage() {
  const router = useRouter();
  const [form, setForm] = useState<CompanyProfileCreate>({
    legal_name: "",
    tax_id: "",
    tax_address: "",
    postal_code: "",
    city: "",
    province: "",
    country: "España",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiGet<CompanyProfile>("/company-profile");
      setForm({
        legal_name: data.legal_name,
        tax_id: data.tax_id,
        tax_address: data.tax_address,
        postal_code: data.postal_code,
        city: data.city,
        province: data.province,
        country: data.country,
      });
    } catch {
      setError("No se pudo cargar el perfil fiscal");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const save = async () => {
    setError(null);
    setSaving(true);
    try {
      await apiPut<CompanyProfile>("/company-profile", form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-slate-500">Cargando...</p>;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Perfil fiscal</h1>
        <Button variant="secondary" onClick={() => router.push("/dashboard")}>
          Volver al dashboard
        </Button>
      </div>

      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
      {saved && (
        <p className="mb-3 text-sm text-green-600">Perfil guardado correctamente.</p>
      )}

      <Card>
        <form onSubmit={(e) => { e.preventDefault(); save(); }} className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Razón social / Nombre comercial"
            type="text"
            value={form.legal_name}
            onChange={(e) => setForm({ ...form, legal_name: e.target.value })}
            required
          />
          <Input
            label="NIF / CIF"
            type="text"
            value={form.tax_id}
            onChange={(e) => setForm({ ...form, tax_id: e.target.value })}
            required
          />
          <Input
            label="Dirección fiscal"
            type="text"
            value={form.tax_address}
            onChange={(e) => setForm({ ...form, tax_address: e.target.value })}
            required
          />
          <Input
            label="Código postal"
            type="text"
            value={form.postal_code}
            onChange={(e) => setForm({ ...form, postal_code: e.target.value })}
            required
          />
          <Input
            label="Población"
            type="text"
            value={form.city}
            onChange={(e) => setForm({ ...form, city: e.target.value })}
            required
          />
          <Input
            label="Provincia"
            type="text"
            value={form.province}
            onChange={(e) => setForm({ ...form, province: e.target.value })}
            required
          />
          <Input
            label="País"
            type="text"
            value={form.country}
            onChange={(e) => setForm({ ...form, country: e.target.value })}
            required
          />
          <div className="sm:col-span-2 flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={load}>
              Descartar
            </Button>
            <Button loading={saving} type="submit">
              Guardar perfil fiscal
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
