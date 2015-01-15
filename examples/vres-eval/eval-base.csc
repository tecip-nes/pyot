<?xml version="1.0" encoding="UTF-8"?>
<simconf>
  <project EXPORT="discard">[APPS_DIR]/mrm</project>
  <project EXPORT="discard">[APPS_DIR]/mspsim</project>
  <project EXPORT="discard">[APPS_DIR]/avrora</project>
  <project EXPORT="discard">[APPS_DIR]/serial_socket</project>
  <project EXPORT="discard">[APPS_DIR]/collect-view</project>
  <project EXPORT="discard">[APPS_DIR]/powertracker</project>
  <simulation>
    <title>Flow-src</title>
    <randomseed>123456</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range>
      <interference_range>100.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events>
      <logoutput>40000</logoutput>
    </events>
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>rplroot</identifier>
      <description>RPL Border Router</description>
      <source EXPORT="discard">[CONFIG_DIR]/br-node/border-router.c</source>
      <commands EXPORT="discard">make border-router.wismote TARGET=wismote</commands>
      <firmware EXPORT="copy">[CONFIG_DIR]/br-node/border-router.wismote</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>wismote2</identifier>
      <description>T-Res Node</description>
      <source EXPORT="discard">[CONFIG_DIR]/tres-node/tres-node.c</source>
      <commands EXPORT="discard">make tres-node.wismote TARGET=wismote</commands>
      <firmware EXPORT="copy">[CONFIG_DIR]/tres-node/tres-node.wismote</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>wismote3</identifier>
      <description>Sensor Node</description>
      <source EXPORT="discard">[CONFIG_DIR]/erbium/er-example-server.c</source>
      <commands EXPORT="discard">make er-example-server.wismote TARGET=wismote</commands>
      <firmware EXPORT="copy">[CONFIG_DIR]/erbium/er-example-server.wismote</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>wismote1</identifier>
      <description>Wismote Mote Type #wismote1</description>
      <source EXPORT="discard">[CONFIG_DIR]/cps-app/cps-control.c</source>
      <commands EXPORT="discard">make cps-control.wismote TARGET=wismote</commands>
      <firmware EXPORT="copy">[CONFIG_DIR]/cps-app/cps-control.wismote</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>wismote4</identifier>
      <description>Wismote Mote Type #wismote4</description>
      <source EXPORT="discard">[CONFIG_DIR]/cps-baseline/cps-base-control.c</source>
      <commands EXPORT="discard">make cps-base-control.wismote TARGET=wismote</commands>
      <firmware EXPORT="copy">[CONFIG_DIR]/cps-baseline/cps-base-control.wismote</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-6.069240694873898</x>
        <y>35.77142594314248</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>1</id>
      </interface_config>
      <motetype_identifier>rplroot</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>70.14274383445378</x>
        <y>21.2291924659058</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>3</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>77.92219276434662</x>
        <y>64.49585239385532</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>4</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>80.35831407158467</x>
        <y>34.39732012110832</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>5</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-31.31038440787168</x>
        <y>19.5410647664925</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>7</id>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspDefaultSerial
        <history>h~;j~;g~;h~;hg~;hn~;f~;g~;f~;</history>
      </interface_config>
      <motetype_identifier>wismote4</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>22.468551165817413</x>
        <y>41.164108935179364</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>8</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-26.308547424623107</x>
        <y>112.16115037336127</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>9</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>20.135192684689677</x>
        <y>109.61202897349852</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>10</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-6.714315296342225</x>
        <y>65.83231518461957</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>11</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>52.48001261165026</x>
        <y>47.789619207565146</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>12</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-3.5926286603404227</x>
        <y>92.51911261697123</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>13</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>2.4894068751449905</x>
        <y>119.75282855582758</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>14</id>
      </interface_config>
      <motetype_identifier>wismote3</motetype_identifier>
    </mote>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.SimControl
    <width>280</width>
    <z>3</z>
    <height>160</height>
    <location_x>1345</location_x>
    <location_y>21</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
      <moterelations>true</moterelations>
      <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.GridVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.TrafficVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.UDGMVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.AddressVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.MoteTypeVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.LEDVisualizerSkin</skin>
      <viewport>2.3082032748930166 0.0 0.0 2.3082032748930166 134.3010348587117 -18.350784943262354</viewport>
    </plugin_config>
    <width>400</width>
    <z>2</z>
    <height>400</height>
    <location_x>1</location_x>
    <location_y>1</location_y>
  </plugin>
  <plugin>
    SerialSocketServer
    <mote_arg>0</mote_arg>
    <width>396</width>
    <z>1</z>
    <height>75</height>
    <location_x>2</location_x>
    <location_y>402</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>ID:3</filter>
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>285</width>
    <z>5</z>
    <height>237</height>
    <location_x>681</location_x>
    <location_y>242</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>/*&#xD;
 * Example Contiki test script (JavaScript).&#xD;
 * A Contiki test script acts on mote output, such as via printf()'s.&#xD;
 * The script may operate on the following variables:&#xD;
 *  Mote mote, int id, String msg&#xD;
 */&#xD;
&#xD;
/* Make test automatically fail (timeout) after 100 simulated seconds */&#xD;
//TIMEOUT(100000); /* milliseconds. no action at timeout */&#xD;
importPackage(java.io);&#xD;
&#xD;
TIMEOUT(70000000)&#xD;
NUM_NODES = 5;&#xD;
CONTROL_NODE = 7;&#xD;
SENSOR_NODE = [3, 4, 5];&#xD;
ACTUATOR_NODE = [9, 14, 10];&#xD;
RUNS = 1000;&#xD;
&#xD;
var sensor_time = 0;//new Array();&#xD;
var sensor_event_count = 0;//new Array();&#xD;
&#xD;
function new_file(str) {&#xD;
    return new FileWriter("firsttest.txt");&#xD;
}&#xD;
&#xD;
function mylog(str)&#xD;
{&#xD;
  log.log(str);&#xD;
  file.write(str);&#xD;
}&#xD;
&#xD;
//returns true is the id is from a sensor node&#xD;
function is_sensor_id()&#xD;
{&#xD;
  for (var i = 0; i &lt;= SENSOR_NODE.length; i++) {&#xD;
    if(id == SENSOR_NODE[i])&#xD;
      return true;&#xD;
  }&#xD;
  return false;&#xD;
}&#xD;
&#xD;
function init_eval()&#xD;
{&#xD;
  sensor_time = 0;&#xD;
  sensor_event_count = 0;&#xD;
&#xD;
    /*for (var i = 0; i &lt;= SENSOR_NODE.length; i++) {&#xD;
    sensor_count[i] = 0;&#xD;
  }*/&#xD;
&#xD;
  actuator_count = 0;&#xD;
  powerlog_count = 0;&#xD;
  //num_samples = 0;&#xD;
  sensor_id = -1;&#xD;
  delay = -1;&#xD;
  script_start_time = -1;&#xD;
  script_end_time = -1;&#xD;
  script_exec_time = -1&#xD;
  miss = 0;&#xD;
  sim_start_time = 0;&#xD;
&#xD;
  file = new_file("");&#xD;
  //powerlog_init();&#xD;
  t = "\t";&#xD;
  mylog("\nSeed: " + sim.getRandomSeed() + "\n");&#xD;
  //print_topology();&#xD;
  mylog(NUM_NODES + " nodes\n");&#xD;
  //mylog(LOGIC_TYPE + " with logic in node " + PYCO_NODE + "\n");&#xD;
  mylog("#\tActuation Latency\t\n");&#xD;
  //mylog("\tID\t[us]\t[us]\n");&#xD;
&#xD;
  GENERATE_MSG(4000, "wait");&#xD;
  YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));&#xD;
}&#xD;
&#xD;
&#xD;
function end_eval()&#xD;
{&#xD;
  //press_all_button();&#xD;
  simtime = time - sim_start_time;&#xD;
  mylog("missed= " + miss + t + "actuator messages" + t + actuator_count + " time " + simtime + "\n");&#xD;
  file.close();&#xD;
  //powerlog_stop();&#xD;
&#xD;
  //if (PYCO_NODE == LAST_PYCO_NODE)&#xD;
  log.testOK();&#xD;
&#xD;
  //GENERATE_MSG(10000, "wait");&#xD;
  //YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));&#xD;
  //press_all_button();&#xD;
  //YIELD_THEN_WAIT_UNTIL(msg.indexOf("Application") != -1);&#xD;
  //PYCO_NODE = id;&#xD;
  //init_eval();&#xD;
}&#xD;
&#xD;
&#xD;
//plugin = mote.getSimulation().getGUI().getStartedPlugin("se.sics.cooja.plugins.analyzers");&#xD;
//log.log("Starting script\n");&#xD;
GENERATE_MSG(60000, "wait");&#xD;
YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));&#xD;
&#xD;
  /* Select time in Radio Logger */&#xD;
  /*plugin = mote.getSimulation().getCooja().getStartedPlugin("org.contikios.cooja.plugins.RadioLogger");&#xD;
  if (plugin != null) {&#xD;
    log.log("RadioLogger: Showing logged radio packet at mid simulation\n");&#xD;
  }*/&#xD;
&#xD;
init_eval();&#xD;
log.log("Init done\n");&#xD;
write(sim.getMoteWithID(7), "go");&#xD;
sim_start_time = time;&#xD;
//press_all_button();&#xD;
YIELD_THEN_WAIT_UNTIL(msg.indexOf("Switching") != -1);&#xD;
log.log("Starting control app\n");&#xD;
&#xD;
while (true) {&#xD;
&#xD;
  if (id==7 &amp;&amp; msg.indexOf("T: ") != -1 /*&amp;&amp; sensor_id == -1*/) {&#xD;
    //sensor_id = id;&#xD;
    sensor_time = time;&#xD;
    sensor_event_count++;&#xD;
    delay = -1;&#xD;
    //script_start_time = -1;&#xD;
    //script_end_time = -1;&#xD;
  }&#xD;
  &#xD;
  /*if (id == PYCO_NODE &amp;&amp; msg.equals("(-") &amp;&amp; script_start_time == -1) {&#xD;
    script_start_time = time;&#xD;
  }&#xD;
  if (id == PYCO_NODE &amp;&amp; msg.equals("-)") &amp;&amp; script_end_time == -1 ) {&#xD;
    script_end_time = time;&#xD;
  }*/&#xD;
    &#xD;
  if (id == 7 &amp;&amp; msg.indexOf("M: ") != -1) {&#xD;
    miss ++;&#xD;
  }&#xD;
&#xD;
&#xD;
  if (id == ACTUATOR_NODE[0] &amp;&amp; msg.indexOf("A: ") != -1 &amp;&amp; delay == -1) {&#xD;
    d0 = time - sensor_time;&#xD;
    //sensor_time = 0;&#xD;
    //actuator_count++;&#xD;
    //script_exec_time = script_end_time - script_start_time;&#xD;
    mylog((actuator_count) + t + d0 + t);&#xD;
    //sensor_id = -1;&#xD;
  }  &#xD;
&#xD;
  /*if (id == ACTUATOR_NODE[1] &amp;&amp; msg.indexOf("A: ") != -1 &amp;&amp; delay == -1) {&#xD;
    d1 = time - sensor_time;&#xD;
    //sensor_time = 0;&#xD;
    //actuator_count++;&#xD;
    //script_exec_time = script_end_time - script_start_time;&#xD;
    mylog(d1 + t);&#xD;
    //sensor_id = -1;&#xD;
  }*/  &#xD;
    &#xD;
        &#xD;
  if (id == ACTUATOR_NODE[2] &amp;&amp; msg.indexOf("A: ") != -1 &amp;&amp; delay == -1) {&#xD;
    delay = time - sensor_time;&#xD;
    sensor_time = 0;&#xD;
    actuator_count++;&#xD;
    //script_exec_time = script_end_time - script_start_time;&#xD;
    //data_size = plugin.getDataTraffic(sensor_time, time);    &#xD;
    mylog(/*(actuator_count) + t + */ delay +/* t + data_size + */"\n");&#xD;
    &#xD;
&#xD;
    //sensor_id = -1;&#xD;
  }&#xD;
&#xD;
  if (actuator_count == RUNS){&#xD;
    end_eval();&#xD;
  }&#xD;
  /*if (msg.indexOf("P: ") != -1) {&#xD;
    powerlog_write();&#xD;
  }&#xD;
&#xD;
  if(powerlog_count == NUM_POWERLOG_ENTRY){&#xD;
    end_eval();&#xD;
  }*/&#xD;
&#xD;
  YIELD();&#xD;
}</script>
      <active>false</active>
    </plugin_config>
    <width>891</width>
    <z>0</z>
    <height>872</height>
    <location_x>583</location_x>
    <location_y>34</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.MoteInterfaceViewer
    <mote_arg>4</mote_arg>
    <plugin_config>
      <interface>Serial port</interface>
      <scrollpos>0,0</scrollpos>
    </plugin_config>
    <width>402</width>
    <z>4</z>
    <height>300</height>
    <location_x>2</location_x>
    <location_y>480</location_y>
  </plugin>
</simconf>

