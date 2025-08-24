
function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }
function fmtMoney(n){ if(n==null) return "—"; return '$' + n.toLocaleString(); }
function partyLabel(p){ return p==='D'?'Democrat':p==='R'?'Republican':p==='I'?'Independent':'—'; }

function fetchFirstJSON(paths){
  return (async () => {
    for (const p of paths){
      try{
        const r = await fetch(p, {cache:'no-store'});
        if (r.ok) return await r.json();
      }catch(e){ /* try next */ }
    }
    throw new Error("All paths failed: " + paths.join(", "));
  })();
}

async function loadMembers(){
  try{
    const local = await fetchFirstJSON([
      'data/members.json',
      '../data/members.json',
      '/data/members.json'
    ]);
    const norm = {};
    for(const m of local){
      const bioguide = m.bioguide || (m.id && m.id.bioguide);
      if(!bioguide) continue;
      const name = m.name || [m.name_first, m.name_last].filter(Boolean).join(' ');
      const party = (m.party||'').trim().toUpperCase().slice(0,1);
      norm[bioguide] = {bioguide, name, state:m.state||'', district:m.district||'', party, photo:m.photo||'images/no-photo.png'};
    }
    return norm;
  }catch(e){ console.error('loadMembers failed', e); return {}; }
}

async function loadVotes(){
  try{
    return await fetchFirstJSON([
      'data/votes.json',
      '../data/votes.json',
      '/data/votes.json'
    ]);
  }catch(e){ console.warn('votes.json missing', e); return {}; }
}

async function loadDonors(){
  try{
    return await fetchFirstJSON([
      'data/donors-by-member.json',
      '../data/donors-by-member.json',
      '/data/donors-by-member.json'
    ]);
  }catch(e){ console.warn('donors file missing', e); return {}; }
}

async function loadAlign(){
  try{
    return await fetchFirstJSON([
      'data/vote-alignments.json',
      '../data/vote-alignments.json',
      '/data/vote-alignments.json'
    ]);
  }catch(e){ console.warn('vote-alignments missing', e); return {}; }
}

async function loadBadges(){
  try{
    return await fetchFirstJSON([
      'data/badges.json',
      '../data/badges.json',
      '/data/badges.json'
    ]);
  }catch(e){ console.warn('badges missing', e); return {}; }
}
