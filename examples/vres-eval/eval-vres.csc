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
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>4.086689245737061</x>
        <y>26.14778538820985</y>
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
        <x>69.5540429935283</x>
        <y>21.02674156039187</y>
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
        <x>61.883941221030945</x>
        <y>65.4654532603079</y>
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
        <x>73.70227114171213</x>
        <y>44.66792631139358</y>
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
        <x>29.91037895428307</x>
        <y>37.98718127175125</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>6</id>
      </interface_config>
      <motetype_identifier>wismote2</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>-10.793263464930359</x>
        <y>6.088528993359758</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>7</id>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspDefaultSerial
        <history>g~;d~;f~;g~;7~;5~;h~;5~;h~;6~;h~;k~;f~;k~;d~;</history>
      </interface_config>
      <motetype_identifier>wismote1</motetype_identifier>
    </mote>
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>50.72856407167398</x>
        <y>42.91590570389462</y>
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
        <x>-11.225537774184621</x>
        <y>78.90688946433288</y>
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
        <x>-26.16336167496906</x>
        <y>107.02128128491823</y>
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
        <x>-1.385072043316907</x>
        <y>107.3847901592595</y>
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
        <x>13.886623735069918</x>
        <y>92.56341144577065</y>
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
        <x>-7.631535515795159</x>
        <y>50.898842379645956</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>13</id>
      </interface_config>
      <motetype_identifier>wismote2</motetype_identifier>
    </mote>
  </simulation>
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
      <viewport>2.944049550188186 0.0 0.0 2.944049550188186 136.7948892226654 3.701652484518763</viewport>
    </plugin_config>
    <width>400</width>
    <z>7</z>
    <height>400</height>
    <location_x>1</location_x>
    <location_y>1</location_y>
  </plugin>
  <plugin>
    SerialSocketServer
    <mote_arg>0</mote_arg>
    <width>386</width>
    <z>9</z>
    <height>75</height>
    <location_x>2</location_x>
    <location_y>405</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>ID:6</filter>
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>484</width>
    <z>5</z>
    <height>453</height>
    <location_x>4</location_x>
    <location_y>484</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>ID:3</filter>
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>285</width>
    <z>8</z>
    <height>237</height>
    <location_x>681</location_x>
    <location_y>242</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.MoteInterfaceViewer
    <mote_arg>5</mote_arg>
    <plugin_config>
      <interface>Serial port</interface>
      <scrollpos>0,0</scrollpos>
    </plugin_config>
    <width>641</width>
    <z>-1</z>
    <height>495</height>
    <location_x>553</location_x>
    <location_y>118</location_y>
    <minimized>true</minimized>
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
ACTUATOR_NODE = [10, 11, 12];&#xD;
RUNS = 500;&#xD;
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
  mylog("#\tSensor\tDelay\tPF time\n");&#xD;
  mylog("\tID\t[us]\t[us]\n");&#xD;
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
  if (id == ACTUATOR_NODE[1] &amp;&amp; msg.indexOf("A: ") != -1 &amp;&amp; delay == -1) {&#xD;
    d1 = time - sensor_time;&#xD;
    //sensor_time = 0;&#xD;
    //actuator_count++;&#xD;
    //script_exec_time = script_end_time - script_start_time;&#xD;
    mylog(d1 + t);&#xD;
    //sensor_id = -1;&#xD;
  }  &#xD;
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
      <active>true</active>
    </plugin_config>
    <width>600</width>
    <z>4</z>
    <height>700</height>
    <location_x>552</location_x>
    <location_y>77</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.MoteInterfaceViewer
    <mote_arg>11</mote_arg>
    <plugin_config>
      <interface>Serial port</interface>
      <scrollpos>0,0</scrollpos>
    </plugin_config>
    <width>649</width>
    <z>2</z>
    <height>590</height>
    <location_x>797</location_x>
    <location_y>336</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>R:</filter>
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>830</width>
    <z>1</z>
    <height>240</height>
    <location_x>474</location_x>
    <location_y>663</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>M:</filter>
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>491</width>
    <z>3</z>
    <height>526</height>
    <location_x>1158</location_x>
    <location_y>3</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.MoteInterfaceViewer
    <mote_arg>5</mote_arg>
    <plugin_config>
      <interface>Serial port</interface>
      <scrollpos>0,0</scrollpos>
    </plugin_config>
    <width>733</width>
    <z>6</z>
    <height>300</height>
    <location_x>36</location_x>
    <location_y>409</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.SimControl
    <width>280</width>
    <z>0</z>
    <height>160</height>
    <location_x>400</location_x>
    <location_y>0</location_y>
  </plugin>
</simconf>

