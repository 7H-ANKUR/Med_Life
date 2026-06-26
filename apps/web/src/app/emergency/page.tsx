"use client";

import React from 'react';
import Link from 'next/link';

export default function EmergencyPage() {
  const toggleSidebar = () => {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('side-nav-overlay');
    if (sidebar && overlay) {
      sidebar.classList.toggle('-translate-x-full');
      overlay.classList.toggle('hidden');
      setTimeout(() => overlay.classList.toggle('opacity-0'), 10);
    }
  };

  return (
    <>
      

<div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
<div className="absolute inset-0 bg-pulse-radial"></div>
<div className="orb-float absolute -top-40 -right-40 w-96 h-96 rounded-full bg-error/10 blur-[100px]"></div>
<div className="orb-float absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-primary/5 blur-[100px]" ></div>
</div>

<header className="fixed top-0 w-full z-40 bg-surface/80 backdrop-blur-xl border-b border-white/20 shadow-[0_4px_30px_rgba(43,76,190,0.04)] h-16 flex justify-between items-center px-gutter">
<div className="flex items-center gap-4">
<button className="p-2 rounded-xl text-primary hover:bg-primary/5 transition-colors active:scale-95 duration-200">
<span className="material-symbols-outlined" data-icon="menu">menu</span>
</button>
<span className="font-display-lg text-headline-md tracking-tight text-primary">MedLife</span>
</div>
<div className="flex items-center gap-2">
<button className="p-2 rounded-xl text-on-surface-variant hover:bg-primary/5 transition-colors active:scale-95 duration-200">
<span className="material-symbols-outlined" data-icon="notifications">notifications</span>
</button>
<button className="p-2 rounded-xl text-on-surface-variant hover:bg-primary/5 transition-colors active:scale-95 duration-200">
<span className="material-symbols-outlined" data-icon="account_circle">account_circle</span>
</button>
</div>
</header>
<main className="pt-16 pb-xl container mx-auto px-gutter max-w-container-max min-h-screen flex flex-col items-center justify-center">

<div className="text-center mb-lg space-y-4">
<div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-error-container text-on-error-container font-label-lg uppercase tracking-wider mb-sm">
<span className="w-2 h-2 rounded-full bg-error animate-pulse"></span>
                Emergency Mode Active
            </div>
<h1 className="font-headline-lg text-headline-lg text-on-background max-w-2xl mx-auto">
                Need Medical Assistance?
            </h1>
<p className="text-on-surface-variant font-body-lg max-w-xl mx-auto">
                One-tap connection to emergency dispatch and real-time medical profile sharing with responders.
            </p>
</div>

<div className="grid grid-cols-1 md:grid-cols-12 gap-md w-full">

<div className="md:col-span-8 glass rounded-[24px] p-lg flex flex-col items-center justify-center text-center relative overflow-hidden group shadow-[0_30px_50px_rgba(186,26,26,0.06)] min-h-[400px]">
<div className="absolute inset-0 bg-gradient-to-br from-error/5 to-transparent pointer-events-none"></div>
<button className="emergency-pulse relative w-48 h-48 md:w-64 md:h-64 rounded-full bg-error text-on-error flex flex-col items-center justify-center gap-2 transition-transform hover:scale-105 active:scale-95 duration-300 z-10 shadow-2xl">
<span className="material-symbols-outlined !text-6xl md:!text-8xl" data-icon="emergency_share" >emergency_share</span>
<span className="font-label-lg text-lg uppercase tracking-[0.2em] font-bold">Call 911</span>
</button>
<div className="mt-lg z-10">
<p className="text-on-surface-variant font-label-lg mb-2">AUTO-SENDING LOCATION &amp; VITALS</p>
<div className="flex items-center gap-4 justify-center">
<div className="flex items-center gap-1.5 text-error">
<span className="material-symbols-outlined text-sm" data-icon="location_on">location_on</span>
<span className="font-label-sm">GPS Active</span>
</div>
<div className="w-px h-4 bg-outline-variant"></div>
<div className="flex items-center gap-1.5 text-primary">
<span className="material-symbols-outlined text-sm" data-icon="monitor_heart">monitor_heart</span>
<span className="font-label-sm">Profile Ready</span>
</div>
</div>
</div>
</div>

<div className="md:col-span-4 flex flex-col gap-md">

<div className="glass rounded-[24px] p-md flex flex-col gap-sm shadow-[0_20px_40px_rgba(43,76,190,0.04)] border-l-4 border-l-primary relative overflow-hidden">
<div className="flex justify-between items-start">
<div>
<span className="font-label-sm text-primary uppercase tracking-widest block mb-1">Nearest ER</span>
<h3 className="font-headline-md text-on-background">St. Jude Medical</h3>
</div>
<div className="bg-primary/10 p-2 rounded-xl text-primary">
<span className="material-symbols-outlined" data-icon="local_hospital">local_hospital</span>
</div>
</div>
<div className="space-y-3 mt-2">
<div className="flex justify-between items-center text-on-surface-variant">
<span className="font-body-md flex items-center gap-2">
<span className="material-symbols-outlined text-sm" data-icon="near_me">near_me</span>
                                1.2 miles away
                            </span>
<span className="font-label-lg text-secondary">6 min drive</span>
</div>
<div className="flex justify-between items-center text-on-surface-variant">
<span className="font-body-md flex items-center gap-2">
<span className="material-symbols-outlined text-sm" data-icon="schedule">schedule</span>
                                Wait Time
                            </span>
<span className="font-label-lg text-tertiary">12 min</span>
</div>
</div>
<div className="h-32 rounded-xl mt-2 overflow-hidden bg-surface-container shadow-inner">
<div className="w-full h-full bg-cover bg-center grayscale opacity-80" data-location="Chicago" ></div>
</div>
<button className="w-full mt-2 py-3 rounded-full bg-primary text-on-primary font-label-lg flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
<span className="material-symbols-outlined text-sm" data-icon="directions">directions</span>
                        Start Navigation
                    </button>
</div>

<div className="glass rounded-[24px] p-md flex items-center gap-4 shadow-sm">
<div className="w-12 h-12 rounded-full border-2 border-primary/20 p-0.5 overflow-hidden">
<img className="w-full h-full object-cover rounded-full" data-alt="Close-up professional portrait of a woman in her 50s with a kind expression, soft natural studio lighting against a clean white clinical background, high-end commercial aesthetic for a medical emergency application." src="https://lh3.googleusercontent.com/aida-public/AB6AXuAFF_2BN4j7IDU5SSCNOoRIiyMAfIu8CRCDpLYfFDm-n7hytRToDzSzo3fQ59wDA6WCBxAkVwLSjV9LWZts1_uh86sKMunUuRJ7ADifuwpdj5a30D_YMVoX-pEq5ZTQtrgeTjl0edB2za8JdywTIXsYufvUw4JLvFyyK59Vfvd4E9-nXPdO1r-gISfDEwcqzZNQh3xAbwGY7FCoDTJY_PKgsUDa-PFhPCgKqIQ8VLvMQQifyv8nbRqpKbet87-vPWMlMlBjiF5hxJ4"/>
</div>
<div className="flex-1">
<h4 className="font-label-lg text-on-background">Sarah Jenkins (Spouse)</h4>
<p className="text-on-surface-variant text-sm">Notify immediately</p>
</div>
<button className="p-2 rounded-full bg-surface-container text-primary hover:bg-primary-container hover:text-on-primary-container transition-all">
<span className="material-symbols-outlined" data-icon="call">call</span>
</button>
</div>
</div>
</div>

<div className="grid grid-cols-1 md:grid-cols-3 gap-md w-full mt-lg">

<button className="group glass p-md rounded-[24px] flex items-center gap-4 hover:bg-primary/5 transition-all">
<div className="w-12 h-12 rounded-2xl bg-secondary-container/20 text-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
<span className="material-symbols-outlined" data-icon="medical_information">medical_information</span>
</div>
<div className="text-left">
<p className="font-label-lg text-on-background">Medical ID</p>
<p className="text-xs text-on-surface-variant">View allergies &amp; blood type</p>
</div>
</button>
<button className="group glass p-md rounded-[24px] flex items-center gap-4 hover:bg-primary/5 transition-all">
<div className="w-12 h-12 rounded-2xl bg-tertiary-container/20 text-tertiary flex items-center justify-center group-hover:scale-110 transition-transform">
<span className="material-symbols-outlined" data-icon="ecg_heart">ecg_heart</span>
</div>
<div className="text-left">
<p className="font-label-lg text-on-background">First Aid AI</p>
<p className="text-xs text-on-surface-variant">Guided instructions for CPR/Choking</p>
</div>
</button>
<button className="group glass p-md rounded-[24px] flex items-center gap-4 hover:bg-primary/5 transition-all">
<div className="w-12 h-12 rounded-2xl bg-error-container/20 text-error flex items-center justify-center group-hover:scale-110 transition-transform">
<span className="material-symbols-outlined" data-icon="sos">sos</span>
</div>
<div className="text-left">
<p className="font-label-lg text-on-background">Silent SOS</p>
<p className="text-xs text-on-surface-variant">Alert authorities without sound</p>
</div>
</button>
</div>

<footer className="mt-xl text-center pb-md">
<p className="text-on-surface-variant text-sm flex items-center justify-center gap-2">
<span className="material-symbols-outlined text-sm" data-icon="verified_user">verified_user</span>
                Secure connection to local emergency infrastructure
            </p>
</footer>
</main>

<aside className="hidden fixed inset-y-0 left-0 w-72 z-50 bg-surface-container-lowest/90 backdrop-blur-2xl border-r border-white/20 shadow-[10px_0_50px_rgba(43,76,190,0.06)] flex flex-col p-md transform -translate-x-full transition-transform duration-300" id="side-nav">
<div className="mb-lg">
<h2 className="font-headline-md text-headline-md text-primary">MedLife Portal</h2>
<p className="text-on-surface-variant font-label-lg">Clinical Dashboard</p>
</div>
<nav className="flex-1 space-y-2">
<a className="flex items-center gap-4 text-on-surface-variant px-4 py-3 hover:bg-surface-container-high transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="search">search</span>
<span className="font-label-lg">Search</span>
</a>
<a className="flex items-center gap-4 text-on-surface-variant px-4 py-3 hover:bg-surface-container-high transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="bookmark">bookmark</span>
<span className="font-label-lg">Saved</span>
</a>
<a className="flex items-center gap-4 text-on-surface-variant px-4 py-3 hover:bg-surface-container-high transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="history">history</span>
<span className="font-label-lg">History</span>
</a>
<a className="flex items-center gap-4 text-on-surface-variant px-4 py-3 hover:bg-surface-container-high transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="person">person</span>
<span className="font-label-lg">Profile</span>
</a>
</nav>
<div className="mt-auto space-y-2 border-t border-outline-variant/20 pt-md">
<a className="flex items-center gap-4 text-on-surface-variant px-4 py-3 hover:bg-surface-container-high transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="settings">settings</span>
<span className="font-label-lg">Settings</span>
</a>
<a className="flex items-center gap-4 text-error px-4 py-3 hover:bg-error-container transition-transform duration-300 hover:translate-x-1 rounded-xl" href="#">
<span className="material-symbols-outlined" data-icon="logout">logout</span>
<span className="font-label-lg">Logout</span>
</a>
</div>
</aside>


    </>
  );
}
