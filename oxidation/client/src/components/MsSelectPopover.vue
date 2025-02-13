<!-- Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS -->

<template>
  <ion-list>
    <ion-item
      id="sort-order-button"
      class="option"
      button
      @click="onOptionClick()"
    >
      {{ sortByAsc ? sortByLabels.asc : sortByLabels.desc }}
      <ion-icon
        :icon="sortByAsc ? arrowUp : arrowDown"
        slot="end"
      />
    </ion-item>
    <ion-item
      class="option"
      :class="{selected: selectedOption?.key === option.key}"
      button
      lines="none"
      v-for="option in options"
      :key="option.key"
      @click="onOptionClick(option)"
    >
      {{ option.label }}
    </ion-item>
  </ion-list>
</template>

<script setup lang="ts">
import { defineProps, ref, Ref } from 'vue';
import {
  IonList,
  IonItem,
  IonIcon,
  popoverController
} from '@ionic/vue';
import {
  arrowUp,
  arrowDown
} from 'ionicons/icons';
import { MsSelectOption, MsSelectSortByLabels, getOptionByKey } from '@/components/MsSelectOption';

const props = defineProps<{
  defaultOption?: string,
  options: MsSelectOption[],
  sortByLabels: MsSelectSortByLabels,
  sortByAsc: boolean
}>();

const sortByAsc: Ref<boolean> = ref(props.sortByAsc);
const selectedOption: Ref<MsSelectOption | undefined> = ref(
  props.defaultOption ? getOptionByKey(props.options, props.defaultOption) : undefined
);

function onOptionClick(option?: MsSelectOption): void {
  if (option) {
    selectedOption.value = option;
  } else {
    sortByAsc.value = !sortByAsc.value;
  }
  popoverController.dismiss({
    option: selectedOption.value,
    sortByAsc: sortByAsc.value
  });
}

</script>

<style lang="scss" scoped>
.option {
  --background-hover: var(--parsec-color-light-primary-50);
  --background-hover-opacity: 1;
  --color-hover: var(--ion-color-tertiary);

  &.selected {
    color: var(--ion-color-tertiary) !important;
    font-weight: bold;
  }
}
</style>
