<template>
  <EasyDataTable v-if="store.state.results.length != 0" :headers="headers" :items="store.state.results"
                 :sort-by="sortBy"
                 :sort-type="sortType"
                 class="customize-table" header-text-direction="left"
                 table-class-name="customize-table">
    <template #item-content="{ content, author, authorurl, avatar, indicator, links}">
      <div class="playeauthor-wrapper">

        <img v-if="avatar" :src="avatar" alt="Avatar" class="avatar"
             onerror="this.src='https://noogle.lol/favicon.ico'"/>
        <img v-else class="avatar" src="@/assets/nostr-purple.svg"/>

        <a :href="authorurl" class="purple" target="_blank">{{ author }}</a>
        <div :data-tip="indicator.time" class="time">
          {{ indicator.time.split("T")[1].split("Z")[0].trim() }}
          {{ indicator.time.split("T")[0].split("-")[2].trim() }}.{{ indicator.time.split("T")[0].split("-")[1].trim() }}.{{ indicator.time.split("T")[0].split("-")[0].trim().slice(2) }}
        </div>
      </div>

<!--      <p>{{ content.substr(0, 320) + "\u2026" }}</p>-->
       <p v-html="StringUtil.parseImages(content).substr(0, 640) + '\u2026'"></p>
      <div style="padding: 2px; text-align: left;">
        <a :href="links.uri" class="menusmall" target="_blank">Nostr Client</a>
        <a :href="links.njump" class="menusmall" target="_blank">NJump</a>
        <a :href="links.highlighter" class="menusmall" target="_blank">Highlighter</a>
        <a :href="links.nostrudel" class="menusmall" target="_blank">Nostrudel</a>
      </div>
    </template>

  </EasyDataTable>


</template>

<script lang="ts" setup>


import type {Header, SortType} from "vue3-easy-data-table";
import store from '../store';
import StringUtil from "@/components/helper/string";

const sortBy = "indicator.time";
const sortType: SortType = "desc";

const headers: Header[] = [
  {text: "Results:", value: "content", fixed: true},
];


</script>

<style scoped>
.operation-wrapper .operation-icon {
  width: 20px;
  cursor: pointer;
}

.playeauthor-wrapper {
  padding: 6px;
  display: flex;
  align-items: center;
  justify-items: center;
}

.menusmall {
  @apply btn text-gray-600 bg-transparent border-transparent tracking-wide;


}

.vue3-easy-data-table__footer.previous-page__click-button {
  height: 100px
}

.time {
  padding: 6px;
  display: flex;
  font-size: 1em;
  align-items: center;
  justify-items: center;
}

.avatar {
  margin-right: 10px;
  display: inline-block;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: inset 0 4px 4px 0 rgb(0 0 0 / 10%);
}

.customize-table {
  width: auto;
  --easy-table-border: 2px solid #000000;
  --easy-table-row-border: 1px solid #000000;

  --easy-table-header-font-size: 14px;
  --easy-table-header-height: 50px;
  --easy-table-header-font-color: bg-accent;
  --easy-table-header-background-color: bg-base;

  --easy-table-header-item-padding: 10px 15px;

  --easy-table-body-even-row-font-color: bg-accenet;
  --easy-table-body-even-row-background-color: bg-base;

  --easy-table-body-row-font-color: bg-accent;
  --easy-table-body-row-background-color: bg-base;
  --easy-table-body-row-height: 50px;
  --easy-table-body-row-font-size: 14px;

  --easy-table-body-row-hover-font-color: bg-accent;
  --easy-table-body-row-hover-background-color: bg-base;

  --easy-table-body-item-padding: 10px 15px;

  --easy-table-footer-background-color: bg-base;
  --easy-table-footer-font-color: bg-accent;
  --easy-table-footer-font-size: 14px;
  --easy-table-footer-padding: 0px 10px;
  --easy-table-footer-height: 50px;

  --easy-table-rows-per-page-selector-width: 70px;
  --easy-table-rows-per-page-selector-option-padding: 10px;
  --easy-table-rows-per-page-selector-z-index: 1;

  --easy-table-scrollbar-track-color: bg-base;
  --easy-table-scrollbar-color: bg-base;
  --easy-table-scrollbar-thumb-color: bg-base;
  --easy-table-scrollbar-corner-color: bg-base;

  --easy-table-loading-mask-background-color: #2d3a4f;
}
</style>