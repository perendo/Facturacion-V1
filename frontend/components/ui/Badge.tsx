import React from "react";

const statusColors: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  sent: "bg-blue-100 text-blue-700",
  paid: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

export default function Badge({ value }: { value: string }) {
  const cls = statusColors[value] || "bg-slate-100 text-slate-700";
  const label: Record<string, string> = {
    draft: "Borrador",
    sent: "Enviada",
    paid: "Pagada",
    cancelled: "Cancelada",
  };
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {label[value] || value}
    </span>
  );
}