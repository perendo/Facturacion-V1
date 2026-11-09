"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { apiGet, apiPost } from "@/lib/api";
import { setToken, setUser } from "@/lib/auth";
import type { User } from "@/lib/types";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "Requerido"),
});
type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const res = await apiPost<{ access_token: string }>("/auth/login", data);
      setToken(res.access_token);
      try {
        const me = await apiGet<User>("/auth/me");
        setUser(me);
      } catch {
        // ignore
      }
      router.push("/dashboard");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error de login";
      setServerError(msg);
    }
  };

  return (
    <Card title="Iniciar sesión">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <Input label="Email" type="email" {...register("email")} error={errors.email?.message} />
        <Input label="Contraseña" type="password" {...register("password")} error={errors.password?.message} />
        {serverError && <p className="text-sm text-red-600">{serverError}</p>}
        <p className="rounded-md bg-slate-100 p-2 text-xs text-slate-600">
          Demo: <span className="font-mono">demo@facturacion.com</span> /{" "}
          <span className="font-mono">demo1234</span>
        </p>
        <Button type="submit" loading={isSubmitting} className="w-full">
          Entrar
        </Button>
        <p className="text-center text-sm text-slate-600">
          ¿No tienes cuenta?{" "}
          <Link href="/register" className="font-medium text-indigo-600 hover:underline">
            Regístrate
          </Link>
        </p>
      </form>
    </Card>
  );
}