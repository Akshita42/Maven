"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

const currencies = ["$", "€", "£", "₹", "¥", "₿"];

export function CurrencyCore({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % currencies.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const dimensions = {
    sm: { core: "w-12 h-12", text: "text-xl", orbit: "w-20 h-20" },
    md: { core: "w-24 h-24", text: "text-5xl", orbit: "w-40 h-40" },
    lg: { core: "w-32 h-32", text: "text-7xl", orbit: "w-56 h-56" },
  };

  return (
    <div className="relative flex items-center justify-center">
      {/* The Orbiting Track */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{
          repeat: Infinity,
          ease: "linear",
          duration: 25,
        }}
        className={`absolute rounded-full border border-white/5 flex items-center justify-center ${dimensions[size].orbit}`}
      >
        {/* The Orbiting Element */}
        <div className="absolute top-0 -translate-y-1/2">
          <AnimatePresence mode="wait">
            <motion.div
              key={index}
              initial={{ opacity: 0, filter: "blur(4px)" }}
              animate={{ opacity: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, filter: "blur(4px)" }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="text-[var(--color-maven-secondary)] text-xl font-light"
            >
              {currencies[index]}
            </motion.div>
          </AnimatePresence>
        </div>
        
        {/* Secondary Orbiting Element */}
        <div className="absolute bottom-0 translate-y-1/2">
          <AnimatePresence mode="wait">
            <motion.div
              key={(index + 3) % currencies.length}
              initial={{ opacity: 0, filter: "blur(4px)" }}
              animate={{ opacity: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, filter: "blur(4px)" }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="text-[var(--color-maven-gray-500)] text-lg font-light"
            >
              {currencies[(index + 3) % currencies.length]}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>

      {/* The Central M */}
      <div
        className={`${dimensions[size].core} rounded-full bg-[var(--color-maven-bg)] shadow-[0_0_50px_rgba(209,58,74,0.15)] border border-[rgba(209,58,74,0.3)] flex items-center justify-center z-10 relative overflow-hidden`}
      >
        <div className="absolute inset-0 bg-gradient-to-tr from-[rgba(209,58,74,0.1)] to-transparent" />
        <span className={`${dimensions[size].text} font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-[var(--color-maven-gray-400)] tracking-tighter select-none`}>
          M
        </span>
      </div>
    </div>
  );
}
