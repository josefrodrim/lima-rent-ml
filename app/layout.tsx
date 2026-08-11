import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "¿Cuánto vale tu alquiler? — lima-rent-ml",
  description:
    "Estima el precio de alquiler de un departamento en Lima Metropolitana con un modelo de Machine Learning explicable.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="antialiased">{children}</body>
    </html>
  );
}
