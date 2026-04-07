import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { Play, Download, Sparkles, Wand2, Activity } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState('');
  const [template, setTemplate] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [taskData, setTaskData] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    let interval;
    if (taskId && taskStatus !== 'completed' && taskStatus !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE_URL}/status/${taskId}`);
          setTaskData(res.data);
          setTaskStatus(res.data.status);
        } catch (error) {
          console.error('Error fetching status', error);
        }
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [taskId, taskStatus]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!url) return;
    try {
      const res = await axios.post(`${API_BASE_URL}/generate`, { url, template });
      setTaskId(res.data.task_id);
      setTaskStatus('pending_generation');
      setTaskData(null);
    } catch (error) {
      console.error('Failed to start generation', error);
      alert('Failed to start generation. Make sure the backend is running.');
    }
  };

  const handleFeedback = async (e) => {
    e.preventDefault();
    if (!feedback || !taskId) return;
    try {
      setTaskStatus('pending_generation');
      const res = await axios.put(`${API_BASE_URL}/feedback/${taskId}`, { feedback_text: feedback });
      setFeedback('');
    } catch (error) {
      console.error('Feedback failed', error);
    }
  };

  const getStatusMessage = () => {
    switch(taskStatus) {
      case 'pending_generation': return 'Analyzing Brand & Crafting Creative Brief...';
      case 'generating': return 'AI Agents Generating Media Assets...';
      case 'synthesizing': return 'Synthesizing Final Cinematic Ad...';
      case 'completed': return 'Ad Generation Complete!';
      case 'failed': return 'Generation Failed.';
      default: return '';
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 font-sans selection:bg-brand-neon selection:text-dark-900 overflow-x-hidden relative">
      {/* Background ambient lighting */}
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-brand-neon/10 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-600/10 blur-[120px] pointer-events-none" />
      
      {/* Header */}
      <header className="fixed top-0 w-full z-50 glass-panel rounded-none border-t-0 border-x-0 !border-b-white/5 py-4 px-8 flex justify-between items-center transition-all">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-neon to-purple-500 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.4)]">
            <Sparkles className="text-dark-900" size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Brand<span className="gradient-text">Sync</span></h1>
        </motion.div>
        <div className="text-sm text-gray-400 flex items-center gap-2">
          <Activity size={16} className="text-brand-neon animate-pulse" />
          AI Studio Ready
        </div>
      </header>

      <main className="max-w-6xl mx-auto pt-32 pb-20 px-6 relative z-10">
        <AnimatePresence mode="wait">
          {!taskId ? (
            <motion.div 
              key="hero"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              className="mt-20 max-w-3xl mx-auto text-center"
            >
              <h2 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight tracking-tight">
                Instantly Generate <br/><span className="gradient-text">Cinematic Ads</span>
              </h2>
              <p className="text-xl text-gray-400 mb-12">
                Paste your product URL and let our unified AI agents orchestrate a broadcast-quality video in minutes.
              </p>
              
              <div className="glass-panel p-2 flex flex-col md:flex-row gap-3 relative overflow-hidden group">
                <div className="absolute inset-0 bg-brand-neon/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <input 
                  type="url"
                  placeholder="https://your-brand.com"
                  className="flex-1 bg-transparent border-0 outline-none px-6 py-4 text-lg placeholder:text-gray-500 relative z-10"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
                <button 
                  onClick={handleGenerate}
                  className="btn-primary flex items-center justify-center gap-2 relative z-10"
                >
                  <Wand2 size={20} />
                  Generate Ad
                </button>
              </div>

              <div className="mt-6 flex justify-center">
                <input 
                  type="text"
                  placeholder="Optional: Brand Vibe (e.g., 'Make it cyberpunk')"
                  className="w-full md:w-2/3 bg-dark-800/50 border border-white/5 rounded-lg px-5 py-3 text-sm focus:border-brand-neon/50 outline-none transition-colors"
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                />
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="dashboard"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-8"
            >
              {/* Left Column: Progress & Brief */}
              <div className="lg:col-span-5 space-y-6">
                <div className="glass-panel p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-200">Pipeline Status</h3>
                    {taskData?.progress && (
                      <span className="text-sm font-mono text-brand-neon tracking-widest">{taskData.progress}%</span>
                    )}
                  </div>
                  
                  {/* Progress Loader Bar */}
                  <div className="w-full h-1.5 bg-dark-900 rounded-full mb-4 overflow-hidden border border-white/5 relative shadow-inner">
                     <motion.div 
                       className="h-full bg-gradient-to-r from-brand-neon to-purple-500 shadow-[0_0_10px_rgba(0,240,255,0.8)]"
                       initial={{ width: '0%' }}
                       animate={{ width: `${taskData?.progress || (taskStatus === 'completed' ? 100 : 0)}%` }}
                       transition={{ ease: "easeOut", duration: 0.5 }}
                     />
                  </div>

                  <div className="p-4 rounded-xl bg-dark-900 border border-white/5 flex items-center gap-4">
                    {taskStatus === 'completed' ? (
                       <div className="w-4 h-4 rounded-full bg-green-500 shadow-[0_0_10px_#22c55e]" />
                    ) : taskStatus === 'failed' ? (
                       <div className="w-4 h-4 rounded-full bg-red-500 shadow-[0_0_10px_#ef4444]" />
                    ) : (
                      <div className="w-4 h-4 rounded-full bg-brand-neon shadow-[0_0_10px_#00f0ff] animate-pulse-slow" />
                    )}
                    <span className="font-medium text-brand-neon capitalize tracking-wide">{getStatusMessage()}</span>
                  </div>
                </div>

                <AnimatePresence>
                  {taskData?.style_contract && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="glass-card p-6 border-l-4 border-l-purple-500"
                    >
                      <div className="flex items-center gap-2 mb-4">
                         <Wand2 size={18} className="text-purple-400" />
                         <h3 className="text-lg font-bold text-gray-100">AI Creative Brief</h3>
                      </div>
                      <div className="space-y-4 text-sm text-gray-300">
                        <div>
                          <strong className="text-purple-300 block mb-1">Visual Style:</strong> 
                          <span className="bg-dark-900 px-3 py-2 rounded-lg block border border-white/5">{taskData.style_contract.visual_style}</span>
                        </div>
                        <div>
                          <strong className="text-purple-300 block mb-1">Narration (35 words):</strong>
                          <span className="bg-dark-900 px-3 py-2 rounded-lg block border border-white/5 italic">"{taskData.style_contract.tts_narration}"</span>
                        </div>
                        <div>
                          <strong className="text-purple-300 block mb-1">Audio Vibe:</strong>
                          <span className="bg-dark-900 px-3 py-2 rounded-lg block border border-white/5">{taskData.style_contract.audio_vibe} ({taskData.style_contract.audio_bpm} BPM)</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {taskStatus === 'completed' && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card p-6 border-l-4 border-l-brand-neon"
                  >
                    <h3 className="text-lg font-bold text-gray-100 mb-3">Re-imagine Ad</h3>
                    <p className="text-sm text-gray-400 mb-4">Want a different vibe? Our AI will rewrite the entire contract to match your new style.</p>
                    <form onSubmit={handleFeedback} className="flex gap-2">
                       <input 
                        type="text"
                        placeholder="e.g. 'Make it a Pixar animation'"
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        className="flex-1 bg-dark-900 border border-white/10 rounded-lg px-4 py-2 outline-none focus:border-brand-neon"
                       />
                       <button className="bg-brand-neon text-dark-900 px-4 py-2 rounded-lg font-semibold hover:bg-brand-hover transition-colors">Apply</button>
                    </form>
                  </motion.div>
                )}
              </div>

              {/* Right Column: Video Player */}
              <div className="lg:col-span-7">
                <div className="glass-panel p-2 h-full flex flex-col min-h-[400px]">
                  {taskStatus === 'completed' && taskData?.final_video_url ? (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="w-full h-full flex flex-col items-center justify-center p-4"
                    >
                       <video 
                         controls 
                         autoPlay
                         className="w-full max-h-[500px] rounded-lg shadow-2xl bg-black"
                         src={`${API_BASE_URL}/video/${taskId}`}
                       />
                       <div className="mt-6 w-full flex justify-end">
                         <a 
                           href={`${API_BASE_URL}/video/${taskId}`}
                           download="BrandSync_Ad.mp4"
                           className="flex items-center gap-2 bg-dark-800 border border-white/10 hover:border-brand-neon text-gray-200 px-5 py-2.5 rounded-lg transition-all"
                         >
                           <Download size={18} />
                           Download Master MP4
                         </a>
                       </div>
                    </motion.div>
                  ) : taskStatus === 'failed' ? (
                     <div className="w-full h-full flex items-center justify-center text-red-400 p-8 text-center bg-dark-900 rounded-xl">
                        Generation Failed. Check backend logs for details.
                     </div>
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center p-12 text-center bg-dark-900 rounded-xl border border-white/5 relative overflow-hidden">
                       <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/micro-grid.png')] opacity-5 mix-blend-overlay" />
                       <div className="w-20 h-20 bg-dark-800 rounded-2xl border border-white/10 flex items-center justify-center mb-6 relative z-10">
                         <div className="absolute inset-0 bg-brand-neon/20 blur-xl rounded-full animate-pulse-slow" />
                         <Play size={32} className="text-brand-neon ml-2 opacity-50" />
                       </div>
                       <h3 className="text-xl font-medium text-gray-200 relative z-10">Constructing Sequence...</h3>
                       <p className="text-sm text-gray-500 mt-2 relative z-10 max-w-sm">
                         We are weaving together motion visuals, high-fidelity images, synthesized narration, and custom score.
                       </p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
