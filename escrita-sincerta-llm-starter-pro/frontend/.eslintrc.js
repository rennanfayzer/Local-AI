module.exports = {
    env: process.env.NODE_ENV, // Uso do ambiente Node (prod ou dev)
    extends: [
        "plugin:react/recommended",
        "plugin:react-hooks/recommended", 
        "standard", // Importando o pacote ESLint padrão para impor as configurações de estilo
    ],
    parserOptions: {parser: "@typescript-eslint/parser"}, // Indicar que usamos TypeScript e a ferramenta @typescript-eslint como analisadora do código. 
    
    plugins: [             // Adicionando o plugin para Shadcn UI, se necessário (Exemplo hipotético)
        "shadcn",        
    ],
  
    rules: {                                // Configuração de regras personalizadas com opções que garantem a consistência e uma aparência profissional. 
        indent: ["error", 2],       // Indentação adequada (Cada nível indente-se por dois espaços)
        semi: [                    // Usar semáforos onde aplicável para melhor legibilidade, exceto em certas situações como anotações ou comentários.
            "error",             // É uma convenção usar um `//` ao invés de `/* ... */`. 
        ],    
        quotes: ["off"],           // Usar aspas simples para strings no TypeScript (considerando que estamos usando TSX)
    },
};