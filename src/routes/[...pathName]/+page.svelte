<script lang="ts">
    import type { PageData } from './$types';
   import {splitText} from '$lib/splitText' 
   import {focusedText, related} from '../searchStores'
   import {page} from '$app/stores'
   import {afterNavigate} from '$app/navigation'
   import { tick } from 'svelte';
    export let data: PageData;
    const segments = splitText(data.pageContent)
    const pageIndex = data.pageIndex;

    const scrollToAndSelectBlock = async () => {
    const searchedText = $page.url.searchParams?.get("search");
    if (!searchedText) return;
    const indexOfText = segments
      // need to trim because db entries are trimmed
      .map((row) => {
        return row.trim();
      })
      ?.indexOf(searchedText);
    if (indexOfText === undefined || indexOfText === null) return;
    /*
    In Overlay.svelte, each block has its id as `editor-block-${indexOfText}`
    We tick to wait for update to trickle down to Overlay

    NB:This function has to be in this component because we want to run it after fetching the file 
    from the electron API.   
    */
    await tick();
    const blockToScrollAndHighlight = document.getElementById(
      `editor-block-${indexOfText}`
    );
    const selection = window.getSelection();
    const range = document.createRange();
    // @ts-ignore
    range.selectNodeContents(blockToScrollAndHighlight);
    selection?.removeAllRanges();
    selection?.addRange(range);
    blockToScrollAndHighlight?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  };

  afterNavigate(scrollToAndSelectBlock);


</script>
<div class='md:w-[26rem] lg:w-[36rem] mx-auto md:p-0 px-5'>
{#each segments as segment, index}
{#if segment.trim().length > 0}
<div id='editor-block-{index}' class='p-1 break-words hover:bg-red-100 transition-colors' 
class:bg-red-100={$focusedText?.trim()===segment?.trim()}
on:click={() => {
   focusedText.set(segment);
   related.set(pageIndex[segment])
}}>{segment}</div>
{:else} 
<br/>
{/if}


{/each}
</div>