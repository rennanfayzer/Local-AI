import Head from 'next/head';
import { Toaster } from 'react-hot-toast';

import './styles/globals.css';

const App = ({ Component, pageProps }) => {
  return (
    <>
      <Head>
        <title>Escrita Sincera - Frontend</title>
        <meta name="description" content="A modern web application for professional writing." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="flex min-h-screen flex-col items-center justify-between p-24">
        <Component {...pageProps} />
      </main>

      <Toaster />
    </>
  );
};

export default App;