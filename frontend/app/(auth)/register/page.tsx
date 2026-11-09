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
  full_name: z.string().optional(),
  email: z.string().email("Email inválido"),
  password: z.string().min(6, "Mínimo 6 caracteres"),
});
type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
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
      await apiPost("/auth/register", data);
      const loginRes = await apiPost<{ access_token: string }>("/auth/login", {
        email: data.email,
        password: data.password,
      });
      setToken(loginRes.access_token);
      try {
        const me = await apiGet<User>("/auth/me");
        setUser(me);
      } catch {
        // ignore
      }
      router.push("/dashboard");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error de registro";
      setServerError(msg);
    }
  };

  return (
    <Card title="Crear cuenta">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <Input label="Nombre completo" {...register("full_name")} error={errors.full_name?.message} />
        <Input label="Email" type="email" {...register("email")} error={errors.email?.message} />
        <Input label="Contraseña" type="password" {...register("password")} error={errors.password?.message} />
        {serverError && <p className="text-sm text-red-600">{serverError}</p>}
        <Button type="submit" loading={isSubmitting} className="w-full">
          Registrarse
        </Button>
        <p className="text-center text-sm text-slate-600">
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="font-medium text-indigo-600 hover:underline">
            Inicia sesión
          </Link>
        </p>
      </form>
    </Card>
  );
}