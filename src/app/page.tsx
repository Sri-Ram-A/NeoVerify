"use client";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { BackgroundLines } from "@/components/ui/background-lines";
import Link from "next/link";

const Index = () => {
  const [showMagnifier, setShowMagnifier] = useState(false);
  const [magnifierPosition, setMagnifierPosition] = useState({ x: 0, y: 0 });

  const handleExploreClick = (e:any) => {
    e.preventDefault();
    setShowMagnifier(true);
    
    // Starting position near the button
    setMagnifierPosition({ x: 50, y: 60 });
    
    // Animate the magnifying glass movement
    const headlineElement = document.querySelector('.headline-text');
    if (headlineElement) {
      const rect = headlineElement.getBoundingClientRect();
      
      // Animation sequence
      setTimeout(() => setMagnifierPosition({ x: 20, y: 20 }), 300);
      setTimeout(() => setMagnifierPosition({ x: 70, y: 10 }), 800);
      setTimeout(() => setMagnifierPosition({ x: 40, y: 30 }), 1300);
      
      // Navigate after animation completes
      setTimeout(() => {
        window.location.href = "/explore";
      }, 1800);
    }
  };

  return (
    <div className="w-full overflow-x-hidden">
      <BackgroundLines className="relative py-20 px-4 bg-black">
        {/* Gemini Twins on left side - modified positioning */}
        <div className="hidden md:block absolute left-0 top-1/2 transform -translate-y-1/2 z-10">
          <img 
            src="/gemini.png" 
            alt="Gemini Twins" 
            className="w-32 lg:w-64 hover:scale-105 transition-transform duration-500"
          />
        </div>

        {/* Mobile version of left image */}
        <div className="md:hidden absolute left-0 top-1/2 transform -translate-y-1/2 z-10">
          <img 
            src="/gemini.png" 
            alt="Gemini Twins" 
            className="w-24 hover:scale-105 transition-transform duration-500 opacity-60"
          />
        </div>

        {/* Mirror image of Gemini Twins on right side - modified positioning */}
        <div className="hidden md:block absolute right-0 top-1/2 transform -translate-y-1/2 z-10">
          <img 
            src="/gemini.png" 
            alt="Gemini Twins Mirror" 
            className="w-32 lg:w-64 hover:scale-105 transition-transform duration-500 scale-x-[-1]"
          />
        </div>

        {/* Mobile version of right image */}
        <div className="md:hidden absolute right-0 top-1/2 transform -translate-y-1/2 z-10">
          <img 
            src="/gemini.png" 
            alt="Gemini Twins Mirror" 
            className="w-24 hover:scale-105 transition-transform duration-500 scale-x-[-1] opacity-60"
          />
        </div>

        {/* Text content in center */}
        <div className="relative z-20 flex flex-col items-center justify-center max-w-4xl mx-auto py-16">
          <div className="relative w-full px-4">
            {/* First image: Top-right of the text */}
            <div className="absolute -top-12 right-4 z-10">
              <img 
                src="/metaLogo.png" 
                alt="meta" 
                className="w-12 md:w-20 opacity-80 hover:opacity-100 transition-opacity duration-300"
              />
            </div>
            
            <h1 className="headline-text bg-clip-text text-transparent text-center bg-gradient-to-b from-white to-neutral-400 text-3xl md:text-5xl lg:text-7xl font-bold tracking-tight mb-6">
              Truth Behind Headlines <br /> BY Knights
            </h1>
            
            {/* Second image: Bottom-left of the text */}
            <div className="absolute -bottom-12 left-4 z-10">
              <img 
                src="/deepseekLogo.png" 
                alt="deepseek" 
                className="w-12 md:w-20 opacity-80 hover:opacity-100 transition-opacity duration-300"
              />
            </div>
            
            {/* Magnifying glass animation */}
            {showMagnifier && (
              <div 
                className="absolute pointer-events-none z-30 transition-all duration-500 ease-out"
                style={{
                  left: `${magnifierPosition.x}%`,
                  top: `${magnifierPosition.y}%`,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                <img 
                  src="/magnifyingGlass.png" 
                  alt="Magnifying Glass" 
                  className="w-12 md:w-20 animate-pulse"
                />
              </div>
            )}
          </div>
          
          <p className="max-w-xl mx-auto text-sm md:text-lg text-neutral-400 text-center mb-10 px-4">
            Are you ready to discover the truth? Delve into these advanced reasoning models
          </p>
          
          {/* Golden button */}
          <Button 
            onClick={handleExploreClick}
            className="bg-gradient-to-r from-amber-500 to-yellow-300 hover:from-amber-600 hover:to-yellow-400 text-black font-bold py-3 px-8 rounded-full text-lg shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-amber-500/30"
          >
            Explore Now
          </Button>
        </div>
      </BackgroundLines>
    </div>
  );
};

export default Index;