import "leaflet/dist/leaflet.css";
import "@/styles/globals.css";
import Head from "next/head";
import { AuthProvider } from "@/context/AuthContext";

export default function App({ Component, pageProps }) {
  return (
    <>
      <Head>
        <title>ITMS Admin Panel</title>
        <meta name="description" content="Intelligent Traffic Management System web dashboard for signal monitoring and control." />
        <meta name="application-name" content="ITMS" />
        <meta name="theme-color" content="#07111f" />
        <meta name="robots" content="noindex,nofollow" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="manifest" href="/manifest.webmanifest" />
      </Head>
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </>
  );
}
