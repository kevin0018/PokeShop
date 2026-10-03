<script setup lang="ts">
defineProps<{ type?: string }>()
</script>

<template>
  <svg
    class="gym-backdrop"
    viewBox="0 0 1200 400"
    preserveAspectRatio="xMidYMid slice"
    aria-hidden="true"
    focusable="false"
  >
    <path class="arena-floor" d="M0 220H1200V400H0Z" />
    <g v-if="type === 'roca'" class="arena-scenery">
      <path d="M0 0H180L150 60 80 110 110 220H0ZM1200 0H1010L1040 65 1120 100 1080 220H1200Z" />
      <path
        d="M230 220L270 140 335 120 390 175 405 220ZM570 220L610 105 700 90 755 165 740 220ZM800 220L835 170 900 155 955 220Z"
      />
      <g class="arena-lines">
        <path
          d="M270 140L310 180 335 120M310 180L300 220M610 105L660 160 700 90M660 160L690 220M835 170L875 200 900 155"
        />
      </g>
      <path
        class="arena-lines"
        d="M410 275L460 265 500 280M730 340L790 325 830 340M70 370L115 355 150 365"
      />
    </g>
    <g v-else-if="type === 'agua'" class="arena-scenery">
      <path d="M120 0H148V220H120ZM1052 0H1080V220H1052Z" />
      <path
        class="arena-lines"
        d="M0 60H1200M0 125H1200M0 190H1200M300 0V220M600 0V220M900 0V220"
      />
      <path d="M250 240H950L1060 400H140Z" />
      <g class="arena-lines">
        <path
          d="M330 270Q375 255 420 270T510 270T600 270T690 270T780 270T870 270M260 325Q305 310 350 325T440 325T530 325T620 325T710 325T800 325T890 325M200 380Q245 365 290 380T380 380T470 380T560 380T650 380T740 380T830 380T920 380"
        />
      </g>
    </g>
    <g v-else-if="type === 'electrico'" class="arena-scenery">
      <path
        class="arena-lines"
        d="M0 45H430V140H520M1200 80H800V160H690M50 0V220M1150 0V220M0 275H1200M0 350H1200M300 220L200 400M600 220V400M900 220L1000 400"
      />
      <path d="M220 220V85H280V220ZM920 220V85H980V220Z" />
      <g class="arena-lines">
        <path
          d="M210 105H290M210 125H290M210 145H290M210 165H290M910 105H990M910 125H990M910 145H990M910 165H990"
        />
      </g>
      <path d="M615 30L555 115H595L580 180 660 85H615Z" />
    </g>
    <g v-else-if="type === 'planta'" class="arena-scenery">
      <path
        class="arena-lines"
        d="M0 110Q600 -100 1200 110M0 195Q600 -30 1200 195M600 0V220M300 0L400 220M900 0L800 220"
      />
      <path d="M150 220V100H165V220ZM1035 220V100H1050V220Z" />
      <ellipse cx="155" cy="90" rx="110" ry="75" />
      <ellipse cx="1045" cy="90" rx="110" ry="75" />
      <path
        d="M280 220Q235 145 280 140Q335 150 310 220ZM890 220Q850 145 890 140Q940 150 925 220Z"
      />
      <path
        class="arena-lines"
        d="M360 400L480 220H720L840 400M0 300Q180 270 310 310M890 310Q1030 270 1200 300"
      />
    </g>
    <g v-else-if="type === 'veneno'" class="arena-scenery">
      <path class="arena-lines" d="M0 60H260V185H430M1200 70H960V185H770M90 0V220M1110 0V220" />
      <path d="M490 220V80Q550 40 610 80V220ZM650 220V120Q700 85 750 120V220Z" />
      <g class="arena-lines">
        <path d="M490 110Q550 140 610 110M490 185Q550 215 610 185M650 145Q700 170 750 145" />
      </g>
      <ellipse cx="590" cy="320" rx="260" ry="50" />
      <g class="arena-lines">
        <circle cx="450" cy="300" r="12" />
        <circle cx="650" cy="320" r="20" />
        <circle cx="740" cy="290" r="10" />
      </g>
    </g>
    <g v-else class="arena-scenery">
      <g class="arena-lines">
        <circle cx="600" cy="130" r="90" />
        <circle cx="600" cy="130" r="62" />
        <path
          d="M600 40L678 175H522ZM600 220L522 85H678ZM260 40L285 85 260 130 235 85ZM940 40L965 85 940 130 915 85ZM0 290H1200M0 370H1200M300 220L180 400M600 220V400M900 220L1020 400"
        />
      </g>
      <path d="M120 220V80H150V220ZM1050 220V80H1080V220Z" />
    </g>
  </svg>
</template>
